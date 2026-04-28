# 🤖 Firmware ESP32-S3 — Xiaozhi AI Voice Assistant (Modifikasi)

<div align="center">

**🌐 [English](#english-version) · 🇮🇩 [Bahasa Indonesia](#versi-bahasa-indonesia)**

[![ESP32-S3](https://img.shields.io/badge/Chip-ESP32--S3-green.svg)](https://www.espressif.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🇮🇩 Versi Bahasa Indonesia

Firmware ESP32-S3 yang dimodifikasi dari [xiaozhi-esp32-music](https://github.com/Maggotxy/xiaozhi-esp32-music) dengan penambahan fitur music streaming dari STB server.

### 🔗 Base Project

Fork & modified from:
- **Maggotxy/xiaozhi-esp32-music**: https://github.com/Maggotxy/xiaozhi-esp32-music
- **xinnan-tech/xiaozhi-esp32**: https://github.com/xinnan-tech/xiaozhi-esp32

### 🎯 Modification Features

- Wake word: **"Hi, ESP"** (model `wn9_hiesp`)
- Integration with `stream_server.py` on STB for playing music from YouTube
- HTTP endpoints `/wake`, `/say`, `/status` for control via Telegram bot
- MAC Address: `XX:XX:XX:XX:XX:XX` (configure in your device)

### 📦 Setup

1. Clone base project from links above
2. Follow official Xiaozhi ESP32 setup guide
3. Configure WiFi and MCP server address (STB IP)

#### Important configuration:
- **WiFi**: adjust SSID and password
- **MCP Endpoint**: point to `ws://STB_IP:PORT/mcp`
- **Static IP ESP32-S3**: `192.168.1.X` (adjust accordingly)

### 🔗 Integration with STB Server

ESP32-S3 communicates with STB via:
1. **WebSocket MCP** — for tool calls (play music, weather, news, etc.)
2. **HTTP `/stream_pcm`** — request audio URL from `stream_server.py`
3. **HTTP `/play`** — stream MP3 audio from YouTube

---

## 🔗 Base Project

Fork & modifikasi dari:
- **Maggotxy/xiaozhi-esp32-music**: https://github.com/Maggotxy/xiaozhi-esp32-music
- **xinnan-tech/xiaozhi-esp32**: https://github.com/xinnan-tech/xiaozhi-esp32

---

## 🎯 Fitur Modifikasi

- Wake word: **"Hi, ESP"** (model `wn9_hiesp`)
- Integrasi dengan `stream_server.py` di STB untuk memutar musik dari YouTube
- HTTP endpoint `/wake`, `/say`, `/status` untuk kontrol via Telegram bot
- MAC Address: `XX:XX:XX:XX:XX:XX` (konfigurasi di perangkat Anda)

---

## 📦 Setup

1. Clone base project dari link di atas
2. Ikuti setup guide resmi Xiaozhi ESP32
3. Konfigurasi WiFi dan alamat MCP server (STB IP)

### Konfigurasi penting:
- **WiFi**: sesuaikan SSID dan password
- **MCP Endpoint**: arahkan ke `ws://STB_IP:PORT/mcp`
- **Static IP ESP32-S3**: `192.168.1.X` (sesuaikan)

---

## 🔗 Integrasi dengan STB Server

ESP32-S3 berkomunikasi dengan STB via:
1. **WebSocket MCP** — untuk tool calls (putar lagu, cuaca, berita, dll)
2. **HTTP `/stream_pcm`** — minta URL audio dari `stream_server.py`
3. **HTTP `/play`** — stream audio MP3 dari YouTube

---

## 🌐 English Version

**ESP32-S3 Firmware** — Xiaozhi AI Voice Assistant (Modified)

ESP32-S3 firmware modified from [xiaozhi-esp32-music](https://github.com/Maggotxy/xiaozhi-esp32-music) with added music streaming feature from STB server.

### 🔗 Base Project

Fork & modified from:
- **Maggotxy/xiaozhi-esp32-music**: https://github.com/Maggotxy/xiaozhi-esp32-music
- **xinnan-tech/xiaozhi-esp32**: https://github.com/xinnan-tech/xiaozhi-esp32

### 🎯 Modification Features

- Wake word: **"Hi, ESP"** (model `wn9_hiesp`)
- Integration with `stream_server.py` on STB for playing music from YouTube
- HTTP endpoints `/wake`, `/say`, `/status` for control via Telegram bot
- MAC Address: `XX:XX:XX:XX:XX:XX` (configure in your device)

### 📦 Setup

1. Clone base project from links above
2. Follow official Xiaozhi ESP32 setup guide
3. Configure WiFi and MCP server address (STB IP)

#### Important configuration:
- **WiFi**: adjust SSID and password
- **MCP Endpoint**: point to `ws://STB_IP:PORT/mcp`
- **Static IP ESP32-S3**: `192.168.1.X` (adjust accordingly)

### 🔗 Integration with STB Server

ESP32-S3 communicates with STB via:
1. **WebSocket MCP** — for tool calls (play music, weather, news, etc.)
2. **HTTP `/stream_pcm`** — request audio URL from `stream_server.py`
3. **HTTP `/play`** — stream MP3 audio from YouTube

