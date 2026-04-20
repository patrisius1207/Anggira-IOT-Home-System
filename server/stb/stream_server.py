from flask import Flask, request, jsonify, Response
import yt_dlp
import subprocess
import urllib.parse
import requests
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

app = Flask(__name__)
lyric_cache = {}

def get_audio_info(song, artist=""):
    query = f"{song} {artist}".strip() if artist else song
    log.info(f"Searching YouTube for: {query}")
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        entry = info['entries'][0]
        log.info(f"Found: {entry.get('title')} ({entry.get('duration')}s)")
        return {
            "url": entry['url'],
            "title": entry.get('title', song),
            "artist": entry.get('uploader', artist),
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

@app.route("/health")
def health():
    return jsonify({"status": "ok", "server": "anggira-music"})

if __name__ == "__main__":
    log.info("Starting music server on 0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, threaded=True)
