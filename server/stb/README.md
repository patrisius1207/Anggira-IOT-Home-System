# 🖥️ STB Server — Anggira AI Core (Termux/Android)

<div align="center">

**🌐 [English](#english-version) · 🇮🇩 [Bahasa Indonesia](#versi-bahasa-indonesia)**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Termux](https://img.shields.io/badge/Platform-Termux-green.svg)](https://termux.com/)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🇮🇩 Versi Bahasa Indonesia

Server utama yang berjalan di STB Android menggunakan **Termux**. Berisi semua logic AI, bot Telegram, music streaming, dan integrasi sensor.

### 📁 Files

| File | Function |
|---|---|
| `anggira.py` | Core: MCP WebSocket server + Telegram STB bot + all AI tools |
| `bot.py` | Telegram bot for wake/control ESP32 Xiaozhi |
| `stream_server.py` | Flask server: YouTube music streaming → MP3 + lyrics |
| `dashboard.py` | Web dashboard to monitor logs from all services (port 8088) |
| `google_auth.py` | OAuth2 Google Calendar setup — run once only |
| `launcher.sh` | Auto-launcher for all services with auto-restart |

### 🔧 Installation (Termux)

#### 1. Install System Dependencies
```bash
pkg update
pkg install python ffmpeg
```

#### 2. Install Python Packages
```bash
pip install python-telegram-bot websockets flask yt-dlp requests
```

#### 3. Detailed Dependencies by File

**anggira.py:**
- `websockets` ← WebSocket server for MCP
- Built-in: `asyncio`, `json`, `urllib`, `datetime`, `threading`

**services.py:**
- All built-in modules ✓
- `asyncio`, `json`, `urllib`, `datetime`, `os`, `subprocess`, `re`, `logging`, `concurrent.futures`

**bot.py:**
- `python-telegram-bot` ← Telegram bot library
- Built-in: `asyncio`, `json`, `logging`, `os`, `random`, `time`, `urllib`, `datetime`

**stream_server.py:**
- `flask` ← Web server for music streaming
- `yt-dlp` ← YouTube downloader
- `requests` ← HTTP requests
- Built-in: `subprocess`, `urllib.parse`, `logging`, `threading`

#### 4. Verify Installation
```bash
python -c "import websockets; print('websockets OK')"
python -c "import telegram; print('python-telegram-bot OK')"
python -c "import flask; print('flask OK')"
python -c "import yt_dlp; print('yt-dlp OK')"
python -c "import requests; print('requests OK')"
```

### ⚙️ Environment Variables

Add to `~/.bashrc`:

```bash
# Telegram
export TELEGRAM_BOT_TOKEN="token_bot_xiaozhi"       # Bot for ESP32/Xiaozhi
export TELEGRAM_STB_TOKEN="token_bot_anggira"        # Bot for STB/Anggira
export TELEGRAM_ALLOWED_USER_ID="123456789"

# AI & API
export OPENROUTER_API_KEY="sk-or-..."
export OPENWEATHER_API_KEY="key_openweather"
export MCP_ENDPOINT="ws://localhost:PORT/mcp"

# Google Calendar
export GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-xxx"
export GOOGLE_TOKEN_FILE="/data/data/com.termux/files/home/google_token.json"

# ESP32
export ESP32_SENSOR_IP="192.168.1.222"    # IP ESP32-C3
export ESP32_IP="192.168.1.XXX"           # IP ESP32-S3 Xiaozhi
export ESP32_PORT="80"
```

### 🚀 Running

```bash
# First time — setup Google Calendar
python ~/anggira/google_auth.py

# Run all services
bash ~/anggira/launcher.sh
```

Or run individually:

```bash
python ~/anggira/anggira.py     # Core AI + MCP
python ~/anggira/bot.py         # Telegram bot Xiaozhi
python ~/anggira/stream_server.py  # Music server
python ~/anggira/dashboard.py   # Web dashboard
```

### 🌐 Ports

| Service | Port |
|---|---|
| Music Stream Server | 8080 |
| Web Log Dashboard | 8088 |

### 🛠️ AI Tools (via MCP)

| Tool | Function |
|---|---|
| `lamp_on` / `lamp_off` | Control terrace lamp via ESP32-C3 |
| `sensor_rumah` | Temperature, humidity, pressure data |
| `get_schedule` / `set_schedule` | Automatic lamp schedule |
| `play_song` | Play music via ESP32 speaker |
| `play_song_stb` | Play music on STB/TV speaker |
| `stop_song_stb` | Stop music on STB |
| `weather` | Salatiga weather (OpenWeatherMap) |
| `news` | Latest Indonesian news |
| `get_calendar` | View Google Calendar schedule |
| `add_calendar_event` | Add event to Calendar |

### 📊 Web Dashboard

Open `http://STB_IP:8088` to monitor logs:
- **Anggira** — core AI logs
- **Stream** — music server logs
- **Bot** — Telegram bot logs

---

## 🔧 Instalasi (Termux)

| File | Fungsi |
|---|---|
| `anggira.py` | Core utama: MCP WebSocket server + Telegram STB bot + semua tools AI |
| `bot.py` | Telegram bot untuk wake/kontrol ESP32 Xiaozhi |
| `stream_server.py` | Flask server: streaming musik YouTube → MP3 + lirik |
| `dashboard.py` | Web dashboard monitor log semua service (port 8088) |
| `google_auth.py` | Setup OAuth2 Google Calendar — jalankan sekali saja |
| `launcher.sh` | Auto-launcher semua service dengan auto-restart |

---

## 🔧 Instalasi (Termux)

### 1. Install System Dependencies
```bash
pkg update
pkg install python ffmpeg
```

### 2. Install Python Packages
```bash
pip install python-telegram-bot websockets flask yt-dlp requests
```

### 3. Detailed Dependencies by File

**anggira.py:**
- `websockets` ← WebSocket server untuk MCP
- Built-in: `asyncio`, `json`, `urllib`, `datetime`, `threading`

**services.py:**
- All built-in modules ✓
- `asyncio`, `json`, `urllib`, `datetime`, `os`, `subprocess`, `re`, `logging`, `concurrent.futures`

**bot.py:**
- `python-telegram-bot` ← Telegram bot library
- Built-in: `asyncio`, `json`, `logging`, `os`, `random`, `time`, `urllib`, `datetime`

**stream_server.py:**
- `flask` ← Web server untuk streaming musik
- `yt-dlp` ← YouTube downloader
- `requests` ← HTTP requests
- Built-in: `subprocess`, `urllib.parse`, `logging`, `threading`

### 4. Verify Installation
```bash
python -c "import websockets; print('websockets OK')"
python -c "import telegram; print('python-telegram-bot OK')"
python -c "import flask; print('flask OK')"
python -c "import yt_dlp; print('yt-dlp OK')"
python -c "import requests; print('requests OK')"
```

---

## ⚙️ Environment Variables

Tambahkan ke `~/.bashrc`:

```bash
# Telegram
export TELEGRAM_BOT_TOKEN="token_bot_xiaozhi"       # Bot untuk ESP32/Xiaozhi
export TELEGRAM_STB_TOKEN="token_bot_anggira"        # Bot untuk STB/Anggira
export TELEGRAM_ALLOWED_USER_ID="123456789"

# AI & API
export OPENROUTER_API_KEY="sk-or-..."
export OPENWEATHER_API_KEY="key_openweather"
export MCP_ENDPOINT="ws://localhost:PORT/mcp"

# Google Calendar
export GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-xxx"
export GOOGLE_TOKEN_FILE="/data/data/com.termux/files/home/google_token.json"

# ESP32
export ESP32_SENSOR_IP="192.168.1.222"    # IP ESP32-C3
export ESP32_IP="192.168.1.XXX"           # IP ESP32-S3 Xiaozhi
export ESP32_PORT="80"
```

---

## 🚀 Menjalankan

```bash
# Pertama kali — setup Google Calendar
python ~/anggira/google_auth.py

# Jalankan semua service
bash ~/anggira/launcher.sh
```

Atau jalankan individual:

```bash
python ~/anggira/anggira.py     # Core AI + MCP
python ~/anggira/bot.py         # Telegram bot Xiaozhi
python ~/anggira/stream_server.py  # Music server
python ~/anggira/dashboard.py   # Web dashboard
```

---

## 🌐 Ports

| Service | Port |
|---|---|
| Music Stream Server | 8080 |
| Web Log Dashboard | 8088 |

---

## 🛠️ Tools AI (via MCP)

| Tool | Fungsi |
|---|---|
| `lamp_on` / `lamp_off` | Kontrol lampu teras via ESP32-C3 |
| `sensor_rumah` | Data suhu, kelembaban, tekanan |
| `get_schedule` / `set_schedule` | Jadwal lampu otomatis |
| `play_song` | Putar musik via speaker ESP32 |
| `play_song_stb` | Putar musik di speaker STB/TV |
| `stop_song_stb` | Stop musik di STB |
| `weather` | Cuaca Salatiga (OpenWeatherMap) |
| `news` | Berita terkini Indonesia |
| `get_calendar` | Lihat jadwal Google Calendar |
| `add_calendar_event` | Tambah event ke Calendar |

---

## 📊 Web Dashboard

Buka `http://STB_IP:8088` untuk monitor log:
- **Anggira** — log core AI
- **Stream** — log music server  
- **Bot** — log Telegram bot

---

## 🌐 English Version

**STB Server** — Anggira AI Core (Termux/Android)

Main server running on Android STB using **Termux**. Contains all AI logic, Telegram bot, music streaming, and sensor integration.

### 📁 Files

| File | Function |
|---|---|
| `anggira.py` | Core: MCP WebSocket server + Telegram STB bot + all AI tools |
| `bot.py` | Telegram bot for wake/control ESP32 Xiaozhi |
| `stream_server.py` | Flask server: YouTube music streaming → MP3 + lyrics |
| `dashboard.py` | Web dashboard to monitor logs from all services (port 8088) |
| `google_auth.py` | OAuth2 Google Calendar setup — run once only |
| `launcher.sh` | Auto-launcher for all services with auto-restart |

### 🔧 Installation (Termux)

#### 1. Install System Dependencies
```bash
pkg update
pkg install python ffmpeg
```

#### 2. Install Python Packages
```bash
pip install python-telegram-bot websockets flask yt-dlp requests
```

#### 3. Detailed Dependencies by File

**anggira.py:**
- `websockets` ← WebSocket server for MCP
- Built-in: `asyncio`, `json`, `urllib`, `datetime`, `threading`

**services.py:**
- All built-in modules ✓
- `asyncio`, `json`, `urllib`, `datetime`, `os`, `subprocess`, `re`, `logging`, `concurrent.futures`

**bot.py:**
- `python-telegram-bot` ← Telegram bot library
- Built-in: `asyncio`, `json`, `logging`, `os`, `random`, `time`, `urllib`, `datetime`

**stream_server.py:**
- `flask` ← Web server for music streaming
- `yt-dlp` ← YouTube downloader
- `requests` ← HTTP requests
- Built-in: `subprocess`, `urllib.parse`, `logging`, `threading`

#### 4. Verify Installation
```bash
python -c "import websockets; print('websockets OK')"
python -c "import telegram; print('python-telegram-bot OK')"
python -c "import flask; print('flask OK')"
python -c "import yt_dlp; print('yt-dlp OK')"
python -c "import requests; print('requests OK')"
```

### ⚙️ Environment Variables

Add to `~/.bashrc`:

```bash
# Telegram
export TELEGRAM_BOT_TOKEN="token_bot_xiaozhi"       # Bot for ESP32/Xiaozhi
export TELEGRAM_STB_TOKEN="token_bot_anggira"        # Bot for STB/Anggira
export TELEGRAM_ALLOWED_USER_ID="123456789"

# AI & API
export OPENROUTER_API_KEY="sk-or-..."
export OPENWEATHER_API_KEY="key_openweather"
export MCP_ENDPOINT="ws://localhost:PORT/mcp"

# Google Calendar
export GOOGLE_CLIENT_ID="xxx.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="GOCSPX-xxx"
export GOOGLE_TOKEN_FILE="/data/data/com.termux/files/home/google_token.json"

# ESP32
export ESP32_SENSOR_IP="192.168.1.222"    # IP ESP32-C3
export ESP32_IP="192.168.1.XXX"           # IP ESP32-S3 Xiaozhi
export ESP32_PORT="80"
```

### 🚀 Running

```bash
# First time — setup Google Calendar
python ~/anggira/google_auth.py

# Run all services
bash ~/anggira/launcher.sh
```

Or run individually:

```bash
python ~/anggira/anggira.py     # Core AI + MCP
python ~/anggira/bot.py         # Telegram bot Xiaozhi
python ~/anggira/stream_server.py  # Music server
python ~/anggira/dashboard.py   # Web dashboard
```

### 🌐 Ports

| Service | Port |
|---|---|
| Music Stream Server | 8080 |
| Web Log Dashboard | 8088 |

### 🛠️ AI Tools (via MCP)

| Tool | Function |
|---|---|
| `lamp_on` / `lamp_off` | Control terrace lamp via ESP32-C3 |
| `sensor_rumah` | Temperature, humidity, pressure data |
| `get_schedule` / `set_schedule` | Automatic lamp schedule |
| `play_song` | Play music via ESP32 speaker |
| `play_song_stb` | Play music on STB/TV speaker |
| `stop_song_stb` | Stop music on STB |
| `weather` | Salatiga weather (OpenWeatherMap) |
| `news` | Latest Indonesian news |
| `get_calendar` | View Google Calendar schedule |
| `add_calendar_event` | Add event to Calendar |

### 📊 Web Dashboard

Open `http://STB_IP:8088` to monitor logs:
- **Anggira** — core AI logs
- **Stream** — music server logs
- **Bot** — Telegram bot logs
