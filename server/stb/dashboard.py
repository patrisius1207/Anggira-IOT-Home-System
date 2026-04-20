import http.server
import json
import os
from urllib.parse import urlparse

ANGGIRA_LOG = os.path.expanduser("~/anggira.log")
STREAM_LOG  = os.path.expanduser("~/stream_server.log")
BOT_LOG     = os.path.expanduser("~/bot.log")

# ================= UI =================
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>STB Logs</title>

<style>
body{
    margin:0;
    background:#020617;
    color:#e2e8f0;
    font-family:monospace;
}

h2{
    margin:10px;
}

pre{
    margin:10px;
    padding:10px;
    background:#0f172a;
    border-radius:10px;
    max-height:250px;
    overflow:auto;
    font-size:12px;
}

button{
    margin:10px;
    padding:10px;
    width:90%;
    background:#2563eb;
    border:none;
    color:white;
    border-radius:8px;
}
</style>
</head>

<body>

<h2>🤖 Anggira</h2>
<button onclick="load('anggira')">Load</button>
<pre id="anggira">...</pre>

<h2>🎵 Stream</h2>
<button onclick="load('stream')">Load</button>
<pre id="stream">...</pre>

<h2>📱 Bot</h2>
<button onclick="load('bot')">Load</button>
<pre id="bot">...</pre>

<script>
async function load(type){
    const r = await fetch('/api/'+type);
    const d = await r.json();
    document.getElementById(type).textContent = d.log;
}

// auto refresh tiap 2 detik
setInterval(()=>{
    load('anggira');
    load('stream');
    load('bot');
},2000);

// first load
load('anggira');
load('stream');
load('bot');
</script>

</body>
</html>
"""

# ================= SERVER =================
class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass

    def read_log(self, path):
        if os.path.exists(path):
            with open(path) as f:
                return ''.join(f.readlines()[-100:])
        return "(kosong)"

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlparse(self.path).path

        if path == "/":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(HTML.encode())

        elif path == "/api/anggira":
            self.send_json({"log": self.read_log(ANGGIRA_LOG)})

        elif path == "/api/stream":
            self.send_json({"log": self.read_log(STREAM_LOG)})

        elif path == "/api/bot":
            self.send_json({"log": self.read_log(BOT_LOG)})

        else:
            self.send_response(404)
            self.end_headers()


# ================= RUN =================
if __name__ == "__main__":
    print("Dashboard jalan di http://0.0.0.0:8088")
    http.server.HTTPServer(("0.0.0.0",8088), Handler).serve_forever()