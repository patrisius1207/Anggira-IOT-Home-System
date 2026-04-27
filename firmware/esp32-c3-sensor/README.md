# 🌡️ Firmware ESP32-C3 Mini — Sensor Rumah & Kontrol Lampu

Firmware untuk **ESP32-C3 Mini** sebagai sensor environment rumah sekaligus pengontrol lampu via servo motor.

---

## 🌐 English Version

**ESP32-C3 Mini Firmware** — Home Environment Sensor & Lamp Control

Firmware for **ESP32-C3 Mini** as home environment sensor and lamp controller via servo motor.

### 🔧 Hardware

| Component | Function |
|---|---|
| ESP32-C3 Mini | Main microcontroller |
| AHT20 (I2C 0x38) | Temperature & humidity sensor |
| BMP280 (I2C 0x76/0x77) | Temperature & air pressure sensor |
| Servo Motor | Press physical lamp switch button |
| Buzzer | WiFi status indicator |

### 📌 Pin Configuration

| Pin | Function |
|---|---|
| GPIO 4 | SDA (I2C) |
| GPIO 5 | SCL (I2C) |
| GPIO 10 | Servo PWM |
| GPIO 6 | Buzzer |

### 📦 Required Libraries (Arduino IDE / PlatformIO)

```
- AsyncTCP
- ESPAsyncWebServer
- Adafruit BMP280
- ESP32Servo
```

### ⚙️ Configuration

Edit WiFi section in `Servotemperature.ino`:

```cpp
const char *ssid     = "YOUR_WIFI_SSID";
const char *password = "YOUR_WIFI_PASSWORD";

// Static IP
IPAddress local_IP(192, 168, 1, 222);
IPAddress gateway(192, 168, 1, 1);
```

### 🌐 HTTP API

Base URL: `http://192.168.1.222`

| Endpoint | Method | Response | Description |
|---|---|---|---|
| `/` | GET | HTML | Web dashboard |
| `/data` | GET | JSON | All sensor + system data |
| `/sensor_rumah` | GET | JSON | Data for Anggira AI |
| `/time` | GET | text | WIB time |
| `/on` | GET | `OK` | Turn lamp on |
| `/off` | GET | `OK` | Turn lamp off |
| `/lamp` | GET | `on`/`off` | Lamp status |
| `/jadwal` | GET | JSON | ON/OFF schedule |
| `/set?on=HH:MM&off=HH:MM` | GET | `OK` | Set schedule |

### Example Response `/sensor_rumah`
```json
{
  "nama": "sensor rumah",
  "temperature": 28.5,
  "humidity": 72.3,
  "pressure": 1013.2,
  "lamp": "on"
}
```

### 🔊 Buzzer Indicator

- **2x short beeps** — WiFi connected successfully
- **3x fast beeps** — WiFi timeout / connection failed

### 🌐 Web Dashboard

Open `http://192.168.1.222` in browser to view:
- Temperature, humidity, pressure data
- Lamp status & control
- ESP32 CPU load & RAM
- Automatic lamp schedule settings

---

## 🔧 Hardware

| Komponen | Fungsi |
|---|---|
| ESP32-C3 Mini | Mikrokontroler utama |
| AHT20 (I2C 0x38) | Sensor suhu & kelembaban |
| BMP280 (I2C 0x76/0x77) | Sensor suhu & tekanan udara |
| Servo Motor | Tekan tombol saklar lampu fisik |
| Buzzer | Indikator status WiFi |

## 📌 Pin Configuration

| Pin | Fungsi |
|---|---|
| GPIO 4 | SDA (I2C) |
| GPIO 5 | SCL (I2C) |
| GPIO 10 | Servo PWM |
| GPIO 6 | Buzzer |

---

## 📦 Library yang Dibutuhkan (Arduino IDE / PlatformIO)

```
- AsyncTCP
- ESPAsyncWebServer
- Adafruit BMP280
- ESP32Servo
```

---

## ⚙️ Konfigurasi

Edit bagian WiFi di `Servotemperature.ino`:

```cpp
const char *ssid     = "SSID_WIFI_KAMU";
const char *password = "PASSWORD_WIFI";

// Static IP
IPAddress local_IP(192, 168, 1, 222);
IPAddress gateway(192, 168, 1, 1);
```

---

## 🌐 HTTP API

Base URL: `http://192.168.1.222`

| Endpoint | Method | Response | Keterangan |
|---|---|---|---|
| `/` | GET | HTML | Web dashboard |
| `/data` | GET | JSON | Semua data sensor + sistem |
| `/sensor_rumah` | GET | JSON | Data untuk Anggira AI |
| `/time` | GET | text | Waktu WIB |
| `/on` | GET | `OK` | Nyalakan lampu |
| `/off` | GET | `OK` | Matikan lampu |
| `/lamp` | GET | `on`/`off` | Status lampu |
| `/jadwal` | GET | JSON | Jadwal ON/OFF |
| `/set?on=HH:MM&off=HH:MM` | GET | `OK` | Set jadwal |

### Contoh Response `/sensor_rumah`
```json
{
  "nama": "sensor rumah",
  "temperature": 28.5,
  "humidity": 72.3,
  "pressure": 1013.2,
  "lamp": "on"
}
```

---

## 🔊 Buzzer Indicator

- **2x beep pendek** — WiFi berhasil terhubung
- **3x beep cepat** — WiFi timeout / gagal connect

---

## 🌐 Web Dashboard

Buka `http://192.168.1.222` di browser untuk melihat:
- Data suhu, kelembaban, tekanan
- Status & kontrol lampu
- CPU load & RAM ESP32
- Pengaturan jadwal lampu otomatis
