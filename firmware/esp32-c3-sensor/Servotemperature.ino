#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <ESP32Servo.h>
#include <time.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#define configUSE_TRACE_FACILITY 1
#define configGENERATE_RUN_TIME_STATS 1

// ================= CPU LOAD =================
uint32_t lastIdle = 0;
uint32_t lastTotal = 0;
uint32_t lastLoopTime = 0;
uint32_t loopTime = 0;
float cpuLoad = 0;
unsigned long lastDebug = 0;

float getCpuLoad() {
  TaskStatus_t taskStatusArray[20];
  volatile UBaseType_t taskCount;
  uint32_t totalRunTime;

  taskCount = uxTaskGetSystemState(taskStatusArray, 10, &totalRunTime);

  if (totalRunTime == 0) return 0;

  float idleTime = 0;

  for (int i = 0; i < taskCount; i++) {
    String name = taskStatusArray[i].pcTaskName;

    if (name.indexOf("IDLE") >= 0) {
      idleTime += taskStatusArray[i].ulRunTimeCounter;
    }
  }

  float cpu = 100.0 - ((idleTime / totalRunTime) * 100.0);

  if (cpu < 0) cpu = 0;
  if (cpu > 100) cpu = 100;

  return cpu;
}

// ================= WIFI =================
const char *ssid = "PET HOUSE-2.4G";
const char *password = "mahbang13";

AsyncWebServer server(80);

// STATIC IP
IPAddress local_IP(192, 168, 1, 222);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress dns(8, 8, 8, 8);

unsigned long wifiLastAttempt = 0;
unsigned long wifiStartAttempt = 0;
bool wifiConnecting = false;

// ================= PIN =================
#define SDA_PIN 4
#define SCL_PIN 5
#define SERVO_PIN 10
#define AHT20_ADDR 0x38
#define BUZZER_PIN 6
#define SERVO_CENTER 75
#define SERVO_RANGE 20

Servo lampServo;

void beep(int durationMs) {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(durationMs);
  digitalWrite(BUZZER_PIN, LOW);
}
// ================= NTP =================
const char *ntpServer = "id.pool.ntp.org";
const long gmtOffset_sec = 7 * 3600;

// ================= SENSOR =================
float humidity = 0;
float tempAHT = 0;
float tempBMP = 0;
float pressure = 0;

Adafruit_BMP280 bmp;
bool bmpOK = false;

// ================= TIMER =================
unsigned long lastSensor = 0;
unsigned long lastTimeCheck = 0;
unsigned long lastRSSI = 0;

// ================= SERVO =================
bool lampState = false;

void lampON() {
  lampServo.write(SERVO_CENTER - SERVO_RANGE);
  lampState = true;
}

void lampOFF() {
  lampServo.write(SERVO_CENTER + SERVO_RANGE);
  lampState = false;
}

// ================= JADWAL =================
int onHour = 18, onMinute = 0;
int offHour = 6, offMinute = 0;

void checkSchedule() {
  struct tm t;
  if (!getLocalTime(&t)) return;

  if (t.tm_hour == onHour && t.tm_min == onMinute && t.tm_sec == 0) lampON();
  if (t.tm_hour == offHour && t.tm_min == offMinute && t.tm_sec == 0) lampOFF();
}

// ================= WIFI =================
void initWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.setTxPower(WIFI_POWER_8_5dBm);
  WiFi.setAutoReconnect(false);
  Serial.println("WiFi INIT...");
}

void handleWiFi() {

  wl_status_t status = WiFi.status();

  // ================= CONNECTED =================
  if (status == WL_CONNECTED) {
    if (wifiConnecting) {
      Serial.println("✅ WiFi Connected!");
      Serial.print("IP: ");
      Serial.println(WiFi.localIP());

      // 🔊 Bunyi sukses (2x)
      beep(100);
      delay(100);
      beep(100);

      wifiConnecting = false;
    }
    return;
  }

  // ================= TIMEOUT =================
  if (wifiConnecting) {
    if (millis() - wifiStartAttempt >= 10000) {

      Serial.println("⏱ Timeout, reset WiFi...");

      // 🔊 Bunyi gagal (3x)
      beep(50);
      delay(50);
      beep(50);
      delay(50);
      beep(50);

      WiFi.disconnect(true);
      wifiConnecting = false;
    }
    return; // penting supaya tidak langsung reconnect di loop yang sama
  }

  // ================= START CONNECT =================
  if (millis() - wifiLastAttempt > 5000) {

    Serial.println("🔄 Start WiFi connect...");

    WiFi.disconnect(false);
    delay(100);

    WiFi.config(local_IP, gateway, subnet, dns);
    WiFi.begin(ssid, password);

    wifiStartAttempt = millis();
    wifiLastAttempt = millis();
    wifiConnecting = true;
  }
}


// ================= SENSOR =================
void resetBMP() {
  Serial.println("RESET BMP280...");
  bmp.begin(0x76) || bmp.begin(0x77);
}
void readAHT20() {
  Wire.beginTransmission(AHT20_ADDR);
  Wire.write(0xAC);
  Wire.write(0x33);
  Wire.write(0x00);
  Wire.endTransmission();
  delay(10);

  if (Wire.requestFrom(AHT20_ADDR, 7) == 7) {
    uint8_t d[7];
    for (int i = 0; i < 7; i++) d[i] = Wire.read();

    uint32_t rawH = ((uint32_t)d[1] << 12) | ((uint32_t)d[2] << 4) | (d[3] >> 4);
    uint32_t rawT = ((uint32_t)(d[3] & 0x0F) << 16) | ((uint32_t)d[4] << 8) | d[5];

    humidity = rawH * 100.0 / 1048576.0;
    tempAHT = rawT * 200.0 / 1048576.0 - 50.0;
  }
}

// ================= TIME =================
String getDateTimeID() {
  struct tm t;
  if (!getLocalTime(&t)) return "Memuat waktu...";

  const char *hari[] = { "Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu" };
  const char *bulan[] = { "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember" };

  char buf[100];
  sprintf(buf, "%02d:%02d:%02d WIB | %s, %02d %s %d",
          t.tm_hour, t.tm_min, t.tm_sec,
          hari[t.tm_wday], t.tm_mday, bulan[t.tm_mon], t.tm_year + 1900);

  return String(buf);
}

// ================= WEB =================
String page() {
  return R"rawliteral(
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body{
  margin:0;
  font-family: 'Segoe UI', sans-serif;
  background: linear-gradient(135deg,#0f2027,#203a43,#2c5364);
  color:white;
  text-align:center;
}

h2{margin-top:15px}
#jam{opacity:0.8}

.grid{
  display:grid;
  grid-template-columns: repeat(auto-fit,minmax(150px,1fr));
  gap:10px;
  padding:10px;
}

.card{
  background: rgba(255,255,255,0.08);
  border-radius:15px;
  padding:15px;
  box-shadow:0 0 10px rgba(0,0,0,0.3);
}

.value{
  font-size:22px;
  font-weight:bold;
  margin-top:5px;
}

button{
  padding:10px 15px;
  border:none;
  border-radius:10px;
  margin:5px;
  font-size:14px;
  cursor:pointer;
}

.on{background:#00c853;color:white}
.off{background:#d50000;color:white}

.indikator{
  width:10px;height:10px;border-radius:50%;
  display:inline-block;margin-left:5px;
}
.active{background:#00e5ff;box-shadow:0 0 8px #00e5ff;}

input{
  padding:8px;
  border-radius:8px;
  border:none;
  margin:5px;
}

</style>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<body>

<h2>🌐 ESP32 SMART DASHBOARD</h2>
<h3 id="jam">--</h3>

<div class="grid">
  <div class="card">
    🌡️ AHT20
    <div class="value"><span id="t1">--</span> °C</div>
  </div>

  <div class="card">
    🌡️ BMP280
    <div class="value"><span id="t2">--</span> °C</div>
  </div>

  <div class="card">
    💧 Humidity
    <div class="value"><span id="h">--</span> %</div>
  </div>

  <div class="card">
    🌬️ Pressure
    <div class="value"><span id="p">--</span> hPa</div>
  </div>
</div>

<div class="grid">

  <div class="card">
    📶 WiFi SSID
    <div class="value" id="ssid">--</div>
  </div>

  <div class="card">
    📡 RSSI
    <div class="value"><span id="rssi">--</span> dBm</div>
  </div>

  <div class="card">
    🧠 CPU Load
    <div class="value"><span id="cpu">--</span> %</div>
  </div>

  <div class="card">
    💾 RAM Free
    <div class="value"><span id="ram">--</span> KB</div>
  </div>

</div>

<div class="card">
<h3>💡 Lampu Teras</h3>
<button class="on" onclick="setLamp('on')">ON <span id="ledOn" class="indikator"></span></button>
<button class="off" onclick="setLamp('off')">OFF <span id="ledOff" class="indikator"></span></button>
</div>

<div class="card">
<h3>⏰ Jadwal Aktif</h3>
ON: <span id="jon">--</span><br>
OFF: <span id="joff">--</span>
</div>

<div class="card">
<h3>⚙️ Set Jadwal</h3>
<input type="time" id="on"><br>
<input type="time" id="off"><br>
<button onclick="save()">Simpan</button>
</div>

<script>

// DATA SENSOR
setInterval(()=>{
fetch('/data').then(r=>r.json()).then(d=>{
ssid.innerText = d.ssid;
rssi.innerText = d.rssi;
cpu.innerText = d.cpu;
ram.innerText = (d.heap / 1024).toFixed(0);
t1.innerText=d.t1.toFixed(1);
t2.innerText=d.t2.toFixed(1);
h.innerText=d.h.toFixed(1);
p.innerText=d.p.toFixed(1);
});
},3000);

// JAM
setInterval(()=>{
fetch('/time').then(r=>r.text()).then(t=>jam.innerText=t);
},1000);

// JADWAL
function loadJadwal(){
fetch('/jadwal').then(r=>r.json()).then(j=>{
jon.innerText=j.on;
joff.innerText=j.off;
});
}
setInterval(loadJadwal,3000);

// SIMPAN
function save(){
let on=document.getElementById("on").value;
let off=document.getElementById("off").value;
fetch(`/set?on=${on}&off=${off}`);
}

// LAMPU
function setLamp(s){fetch('/'+s);}

function updateLamp(){
fetch('/lamp').then(r=>r.text()).then(s=>{
ledOn.classList.remove("active");
ledOff.classList.remove("active");
if(s=="on") ledOn.classList.add("active");
else ledOff.classList.add("active");
});
}
setInterval(updateLamp,1000);
updateLamp();

</script>

</body>
</html>
)rawliteral";
}

// ================= SETUP =================

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);  // jangan 400k
  bmpOK = bmp.begin(0x76) || bmp.begin(0x77);

  bmp.setSampling(
    Adafruit_BMP280::MODE_NORMAL,
    Adafruit_BMP280::SAMPLING_X1,
    Adafruit_BMP280::SAMPLING_X4,
    Adafruit_BMP280::FILTER_OFF,
    Adafruit_BMP280::STANDBY_MS_250);
  lampServo.attach(SERVO_PIN);
  lampServo.write(SERVO_CENTER);

  initWiFi();
  configTime(gmtOffset_sec, 0, ntpServer);
  vTaskDelay(1000 / portTICK_PERIOD_MS);
 //================= BUZZER ==============
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);


  // ================= ROUTES =================

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/html", page());
  });

  server.on("/data", HTTP_GET, [](AsyncWebServerRequest *request) {
    char json[256];
    snprintf(json, sizeof(json),
             "{\"t1\":%.1f,\"t2\":%.1f,\"h\":%.1f,\"p\":%.1f,"
             "\"rssi\":%d,\"heap\":%d,\"cpu\":%.1f,\"ssid\":\"%s\"}",
             tempAHT, tempBMP, humidity, pressure,
             WiFi.RSSI(), ESP.getFreeHeap(),
             getCpuLoad(),
             WiFi.SSID().c_str());

    request->send(200, "application/json", json);
  });

  server.on("/time", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", getDateTimeID());
  });

  server.on("/lamp", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", lampState ? "on" : "off");
  });


  server.on("/jadwal", HTTP_GET, [](AsyncWebServerRequest *request) {
    char onBuf[6];
    char offBuf[6];

    sprintf(onBuf, "%02d:%02d", onHour, onMinute);
    sprintf(offBuf, "%02d:%02d", offHour, offMinute);

    String json = "{\"on\":\"" + String(onBuf) + "\",\"off\":\"" + String(offBuf) + "\"}";

    request->send(200, "application/json", json);
  });

  server.on("/set", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam("on") && request->hasParam("off")) {
      String on = request->getParam("on")->value();
      String off = request->getParam("off")->value();

      sscanf(on.c_str(), "%d:%d", &onHour, &onMinute);
      sscanf(off.c_str(), "%d:%d", &offHour, &offMinute);
    }

    request->send(200, "text/plain", "OK");
  });

  server.on("/on", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial.println("LAMPU ON");
    lampON();
    request->send(200, "text/plain", "OK");
  });

  server.on("/off", HTTP_GET, [](AsyncWebServerRequest *request) {
    Serial.println("LAMPU OFF");
    lampOFF();
    request->send(200, "text/plain", "OK");
  });
 
  server.on("/sensor_rumah", HTTP_GET, [](AsyncWebServerRequest *request) {

  String json =
  "{"
  "\"nama\":\"sensor rumah\","
  "\"temperature\":" + String(tempAHT,1) + ","
  "\"humidity\":" + String(humidity,1) + ","
  "\"pressure\":" + String(pressure,1) + ","
  "\"lamp\":\"" + String(lampState ? "on" : "off") + "\""
  "}";

  request->send(200, "application/json", json);
  });
  server.begin();
}


void loop() {

  handleWiFi();
  

  // ================= SENSOR =================
  if (millis() - lastSensor > 3000) {

    readAHT20();

    if (bmpOK) {
      float newTemp = bmp.readTemperature();
      float newPress = bmp.readPressure() / 100.0;

      tempBMP = (tempBMP * 0.7) + (newTemp * 0.3);
      pressure = (pressure * 0.7) + (newPress * 0.3);

      // VALIDASI biar gak stuck
      if (newTemp > -40 && newTemp < 85 &&
          newPress > 300 && newPress < 1100) {

        tempBMP = newTemp;
        pressure = newPress;
      }
    }

    lastSensor = millis();
  }

  // ================= JADWAL =================
  if (millis() - lastTimeCheck > 1000) {
    checkSchedule();
    lastTimeCheck = millis();
  }

  delay(5);
}