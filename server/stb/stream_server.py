from flask import Flask, request, jsonify, Response
import yt_dlp
import subprocess
import urllib.parse
import requests
import logging
import threading

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

# Track proses mpv yang sedang berjalan
local_player_process = None
local_player_lock = threading.Lock()

app = Flask(__name__)
lyric_cache = {}

def get_audio_info(song, artist=""):
    raw_query = f"{song} {artist}".strip() if artist else song
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'jsruntimes': ['node'],
        'default_search': 'auto',
        'nocheckcertificate': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if song.startswith("http://") or song.startswith("https://"):
            log.info(f"Fetching audio info from URL: {song}")
            info = ydl.extract_info(song, download=False)
            if isinstance(info, dict) and info.get('entries'):
                info = info['entries'][0]
        else:
            log.info(f"Searching YouTube for: {raw_query}")
            info = ydl.extract_info(f"ytsearch:{raw_query}", download=False)
            if isinstance(info, dict) and info.get('entries'):
                info = info['entries'][0]

        if not isinstance(info, dict) or 'url' not in info:
            raise ValueError(f"No audio URL found for {song}")

        log.info(f"Found: {info.get('title')} ({info.get('duration')}s)")
        return {
            "url": info['url'],
            "title": info.get('title', song),
            "artist": info.get('uploader', artist),
        }

def fetch_lyrics(song, artist=""):
    try:
        params = {"track_name": song, "artist_name": artist}
        resp = requests.get("https://lrclib.net/api/search", 
                           params=params, timeout=5)
        if resp.status_code == 200:
            results = resp.json()
            for r in results:
                if r.get("syncedLyrics"):
                    log.info(f"Found synced lyrics for: {song}")
                    return r["syncedLyrics"]
            if results:
                return results[0].get("plainLyrics", "")
    except Exception as e:
        log.warning(f"Lyric fetch failed: {e}")
    return ""

@app.route("/stream_pcm")
def stream_pcm():
    song = request.args.get("song", "").strip()
    artist = request.args.get("artist", "").strip()
    
    # Log all headers from ESP32 for debugging
    log.info(f"=== /stream_pcm request ===")
    log.info(f"Song: '{song}', Artist: '{artist}'")
    log.info(f"Client IP: {request.remote_addr}")
    for k, v in request.headers:
        if k.startswith("X-"):
            log.info(f"  {k}: {v}")

    if not song:
        return jsonify({"error": "Missing song parameter"}), 400

    try:
        info = get_audio_info(song, artist)
        base_url = "http://192.168.1.3:8080"
        encoded_url = urllib.parse.quote(info["url"])

        lyrics = fetch_lyrics(song, artist)
        lyric_url = ""
        if lyrics:
            cache_key = f"{song}_{artist}"
            lyric_cache[cache_key] = lyrics
            lyric_url = (f"{base_url}/lyrics"
                        f"?song={urllib.parse.quote(song)}"
                        f"&artist={urllib.parse.quote(artist)}")

        response_data = {
            "title": info["title"],
            "artist": info["artist"],
            "audio_url": f"{base_url}/play?url={encoded_url}",
            "lyric_url": lyric_url
        }
        log.info(f"Returning: title='{info['title']}', lyric={'yes' if lyric_url else 'no'}")
        return jsonify(response_data)

    except Exception as e:
        log.error(f"stream_pcm error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route("/lyrics")
def lyrics():
    song = request.args.get("song", "")
    artist = request.args.get("artist", "")
    key = f"{song}_{artist}"
    content = lyric_cache.get(key, "")
    log.info(f"Lyrics requested for '{song}': {'found' if content else 'not found'}")
    return Response(content, content_type="text/plain; charset=utf-8")

@app.route("/play")
def play():
    url = request.args.get("url", "")
    if not url:
        return jsonify({"error": "Missing url"}), 400
    
    log.info(f"Streaming audio to {request.remote_addr}")

    def generate():
        command = [
            "ffmpeg",
            "-reconnect", "1",
            "-reconnect_streamed", "1", 
            "-reconnect_delay_max", "5",
            "-i", url,
            "-f", "mp3",
            "-acodec", "libmp3lame",
            "-ab", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-vn",
            "-"
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        try:
            total = 0
            while True:
                data = process.stdout.read(4096)
                if not data:
                    break
                total += len(data)
                yield data
            log.info(f"Stream complete: {total} bytes sent")
        finally:
            process.kill()

    return Response(generate(), content_type="audio/mpeg")

@app.route("/play_local")
def play_local():
    """
    Putar lagu langsung di speaker STB menggunakan mpv.
    Otomatis stop lagu sebelumnya jika ada yang sedang main.
    """
    global local_player_process

    song = request.args.get("song", "").strip()
    artist = request.args.get("artist", "").strip()

    if not song:
        return jsonify({"error": "Missing song parameter"}), 400

    log.info(f"=== /play_local request: song='{song}', artist='{artist}' ===")

    try:
        # Cari audio URL dulu
        info = get_audio_info(song, artist)
        audio_url = info["url"]
        title = info["title"]

        log.info(f"Playing locally: {title}")
        log.info(f"Audio URL: {audio_url[:80]}...")

        # Simpan ke cache lirik juga
        lyrics = fetch_lyrics(song, artist)
        if lyrics:
            cache_key = f"{song}_{artist}"
            lyric_cache[cache_key] = lyrics

        # Stop proses sebelumnya jika masih jalan
        with local_player_lock:
            if local_player_process and local_player_process.poll() is None:
                log.info("Stopping previous local playback")
                local_player_process.terminate()
                try:
                    local_player_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    local_player_process.kill()

            # Jalankan mpv untuk play audio di STB
            # --no-video   : audio only
            # --volume=100 : volume penuh
            # --really-quiet: suppress output
            cmd = [
                "mpv",
                "--no-video",
                "--audio-device=opensles",
                "--volume=100",
                "--really-quiet",
                audio_url
            ]

            local_player_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log.info(f"mpv started with PID: {local_player_process.pid}")

        return jsonify({
            "status": "playing",
            "song": song,
            "title": title,
            "artist": info["artist"],
            "pid": local_player_process.pid
        })

    except FileNotFoundError:
        # mpv tidak terinstall, coba fallback ke ffplay
        log.warning("mpv not found, trying ffplay...")
        try:
            with local_player_lock:
                if local_player_process and local_player_process.poll() is None:
                    local_player_process.terminate()

                cmd = [
                    "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-volume", "100",
                    audio_url
                ]
                local_player_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            return jsonify({"status": "playing", "song": song, "player": "ffplay"})
        except Exception as e:
            log.error(f"ffplay also failed: {e}")
            return jsonify({"error": "mpv dan ffplay tidak ditemukan. Install dengan: apt install mpv"}), 500

    except Exception as e:
        log.error(f"play_local error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/stop_local", methods=["GET", "POST"])
def stop_local():
    """Stop pemutaran lagu lokal di STB."""
    global local_player_process

    with local_player_lock:
        if local_player_process and local_player_process.poll() is None:
            local_player_process.terminate()
            try:
                local_player_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                local_player_process.kill()
            log.info("Local playback stopped")
            return jsonify({"status": "stopped"})
        else:
            return jsonify({"status": "not_playing"})



@app.route("/stream_radio")
def stream_radio():
    """
    Putar internet radio via speaker ESP32.
    URL stream radio langsung di-pipe FFmpeg → streaming ke ESP32.
    """
    radio_url = request.args.get("url", "").strip()
    name = request.args.get("name", "Radio").strip()

    if not radio_url:
        return jsonify({"error": "Missing url parameter"}), 400

    log.info(f"=== /stream_radio: name='{name}' url='{radio_url}' ===")
    log.info(f"Client IP: {request.remote_addr}")

    def generate():
        command = [
            "ffmpeg",
            "-reconnect", "1",
            "-reconnect_streamed", "1",
            "-reconnect_delay_max", "5",
            "-i", radio_url,
            "-f", "mp3",
            "-acodec", "libmp3lame",
            "-ab", "128k",
            "-ar", "44100",
            "-ac", "2",
            "-vn",
            "-"
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        try:
            total = 0
            while True:
                data = process.stdout.read(4096)
                if not data:
                    break
                total += len(data)
                yield data
            log.info(f"Radio stream ended: {total} bytes sent")
        finally:
            process.kill()

    return Response(generate(), content_type="audio/mpeg")


@app.route("/play_radio")
def play_radio():
    """
    Putar internet radio langsung di speaker STB menggunakan mpv.
    Otomatis stop pemutaran sebelumnya (musik atau radio).
    """
    global local_player_process

    radio_url = request.args.get("url", "").strip()
    name = request.args.get("name", "Radio").strip()

    if not radio_url:
        return jsonify({"error": "Missing url parameter"}), 400

    log.info(f"=== /play_radio: name='{name}' ===")

    try:
        with local_player_lock:
            if local_player_process and local_player_process.poll() is None:
                log.info("Stopping previous playback before radio")
                local_player_process.terminate()
                try:
                    local_player_process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    local_player_process.kill()

            cmd = ["mpv", "--no-video", "--audio-device=opensles", "--volume=100", "--really-quiet", radio_url]
            local_player_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            log.info(f"Radio mpv PID: {local_player_process.pid}")

        return jsonify({
            "status": "playing",
            "name": name,
            "url": radio_url,
            "pid": local_player_process.pid
        })

    except FileNotFoundError:
        log.warning("mpv not found, trying ffplay...")
        try:
            with local_player_lock:
                if local_player_process and local_player_process.poll() is None:
                    local_player_process.terminate()
                cmd = ["ffplay", "-nodisp", "-autoexit", "-volume", "100", radio_url]
                local_player_process = subprocess.Popen(
                    cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            return jsonify({"status": "playing", "name": name, "player": "ffplay"})
        except Exception as e:
            return jsonify({"error": "mpv dan ffplay tidak ditemukan"}), 500

    except Exception as e:
        log.error(f"play_radio error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/stop_radio", methods=["GET", "POST"])
def stop_radio():
    """
    Stop radio di STB. Menggunakan local_player_process yang sama dengan
    stop_local — cukup satu proses mpv untuk radio maupun musik STB.
    """
    global local_player_process

    with local_player_lock:
        if local_player_process and local_player_process.poll() is None:
            local_player_process.terminate()
            try:
                local_player_process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                local_player_process.kill()
            log.info("Radio playback stopped")
            return jsonify({"status": "stopped"})
        else:
            return jsonify({"status": "not_playing"})



# ================= PLAYLIST =================
import json as _json
import os as _os

PLAYLIST_FILE = _os.path.join(_os.path.expanduser("~"), "anggira", "playlists.json")

_playlist_state = {
    "current_playlist": None,   # nama playlist aktif
    "queue":            [],     # list of {"song": ..., "artist": ...}
    "index":            0,      # index lagu sekarang
    "playing":          False,
}
_playlist_lock = threading.Lock()

def _load_playlists() -> dict:
    if _os.path.exists(PLAYLIST_FILE):
        try:
            with open(PLAYLIST_FILE) as f:
                return _json.load(f)
        except Exception:
            pass
    return {}

def _save_playlists(data: dict):
    _os.makedirs(_os.path.dirname(PLAYLIST_FILE), exist_ok=True)
    with open(PLAYLIST_FILE, "w") as f:
        _json.dump(data, f, indent=2, ensure_ascii=False)

def _play_next_in_playlist():
    """Putar lagu berikutnya di queue. Dipanggil oleh thread monitor."""
    global local_player_process
    with _playlist_lock:
        state = _playlist_state
        if not state["playing"] or state["index"] >= len(state["queue"]):
            state["playing"] = False
            log.info("Playlist selesai")
            return
        track = state["queue"][state["index"]]
        state["index"] += 1

    song   = track.get("song", "")
    artist = track.get("artist", "")
    log.info(f"Playlist: [{state['index']}/{len(state['queue'])}] {song} - {artist}")

    try:
        info = get_audio_info(song, artist)
        cmd  = ["mpv", "--no-video", "--audio-device=opensles",
                "--volume=100", "--really-quiet", info["url"]]

        with local_player_lock:
            if local_player_process and local_player_process.poll() is None:
                local_player_process.terminate()
                try: local_player_process.wait(timeout=3)
                except subprocess.TimeoutExpired: local_player_process.kill()
            local_player_process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        # Monitor selesai lalu lanjut lagu berikutnya
        def _monitor(proc):
            proc.wait()
            with _playlist_lock:
                if _playlist_state["playing"]:
                    _play_next_in_playlist()
        threading.Thread(target=_monitor, args=(local_player_process,), daemon=True).start()

    except Exception as e:
        log.error(f"Playlist play error: {e}")
        # Skip ke lagu berikutnya
        _play_next_in_playlist()


@app.route("/play_playlist")
def play_playlist():
    """Mulai putar playlist berdasarkan nama. ?name=santai&shuffle=true"""
    name    = request.args.get("name", "").strip().lower()
    shuffle = request.args.get("shuffle", "false").lower() == "true"

    playlists = _load_playlists()
    # Case-insensitive match
    key = next((k for k in playlists if k.lower() == name), None)
    if not key:
        available = ", ".join(playlists.keys()) or "kosong"
        return jsonify({"error": f"Playlist '{name}' tidak ada. Tersedia: {available}"}), 404

    tracks = playlists[key].get("tracks", [])
    if not tracks:
        return jsonify({"error": "Playlist kosong"}), 400

    if shuffle:
        import random
        tracks = tracks.copy()
        random.shuffle(tracks)

    with _playlist_lock:
        _playlist_state["current_playlist"] = key
        _playlist_state["queue"]            = tracks
        _playlist_state["index"]            = 0
        _playlist_state["playing"]          = True

    log.info(f"Memulai playlist '{key}' ({len(tracks)} lagu, shuffle={shuffle})")
    _play_next_in_playlist()

    return jsonify({
        "status":   "playing",
        "playlist": key,
        "total":    len(tracks),
        "shuffle":  shuffle,
        "first":    tracks[0].get("song", "") if tracks else ""
    })


@app.route("/playlist_next")
def playlist_next():
    """Skip ke lagu berikutnya."""
    with _playlist_lock:
        if not _playlist_state["playing"]:
            return jsonify({"status": "not_playing"})

    # Stop current mpv, monitor akan trigger next otomatis
    global local_player_process
    with local_player_lock:
        if local_player_process and local_player_process.poll() is None:
            local_player_process.terminate()

    return jsonify({"status": "skipped"})


@app.route("/playlist_stop")
def playlist_stop():
    """Stop playlist."""
    global local_player_process
    with _playlist_lock:
        _playlist_state["playing"] = False
        _playlist_state["queue"]   = []

    with local_player_lock:
        if local_player_process and local_player_process.poll() is None:
            local_player_process.terminate()
            try: local_player_process.wait(timeout=3)
            except subprocess.TimeoutExpired: local_player_process.kill()

    return jsonify({"status": "stopped"})


@app.route("/playlist_status")
def playlist_status():
    """Status playlist saat ini."""
    with _playlist_lock:
        state = _playlist_state
        idx   = state["index"]
        queue = state["queue"]
        current = queue[idx - 1] if idx > 0 and queue else {}
        return jsonify({
            "playing":          state["playing"],
            "playlist":         state["current_playlist"],
            "current_index":    idx,
            "total":            len(queue),
            "current_song":     current.get("song", ""),
            "current_artist":   current.get("artist", ""),
        })


@app.route("/api/playlists", methods=["GET"])
def api_get_playlists():
    return jsonify(_load_playlists())


@app.route("/api/playlists", methods=["POST"])
def api_save_playlists():
    data = request.get_json()
    _save_playlists(data)
    return jsonify({"ok": True})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "server": "anggira-music"})

if __name__ == "__main__":
    log.info("Starting music server on 0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, threaded=True)