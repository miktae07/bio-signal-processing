
// #include <Wire.h>
// #include "MAX30105.h"
// #include "heartRate.h"
// #include <Arduino.h>
// #include <string.h>
// #include <time.h>
// //---------------------------------------------------------------
// #include "WiFi.h"
// #include <FirebaseESP32.h>
// #include <WiFiClient.h>


// #define FIREBASE_HOST "https://esp32-9c871-default-rtdb.firebaseio.com/"
// #define FIREBASE_AUTH "AIzaSyDneFPslsW4O0-3TGLV5yAWFvGaRbdttuY"

// // Múi giờ Việt Nam là GMT+7 => offset = 7*3600
// const long  gmtOffset_sec = 7 * 3600;
// const int   daylightOffset_sec = 0;
// const char* ssid = "TuNaTech 2.4G"; // Thay đổi SSID của bạn
// const char* password = "123456789"; // Thay đổi mật khẩu của bạn

// FirebaseData fbdo;
// FirebaseAuth auth;
// FirebaseConfig config;
// String path = "/";
// //---------------------------------------------------------------
// MAX30105 particleSensor;

// const byte RATE_SIZE = 4;
// byte rates[RATE_SIZE];
// byte rateSpot = 0;
// long lastBeat = 0;

// float beatsPerMinute;
// int beatAvg;



// uint64_t lastMicros = 0;
// const uint64_t intervalMicros = 5000000; // 10 giây


// typedef struct
// {
//   float SpO2;
//   float beatsPerMinute;
//   int beatAvg;
// }Electrocardiogram;

// typedef struct
// {
//   int irValue;
//   int redValue;
//   int adcValue;
// }raw_data;

// void setup() 
// {
//   Serial.begin(115200);
//   Wire.begin(21, 22); // hoặc bỏ nếu dùng Arduino Uno

//   if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) 
//   {
//     Serial.println("Không tìm thấy cảm biến MAX30105.");
//     while (1);
//   }
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// // Kết nối Wi-Fi
//  WiFi.begin(ssid, password);

//   while (WiFi.status() != WL_CONNECTED) 
//   {
//     delay(500);
//     Serial.print(".");
//   }
//   Serial.println("WiFi connected!");
//  // Cấu hình NTP
//   configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org");

//   // Đợi đồng bộ thời gian
//   struct tm timeinfo;
//   if (!getLocalTime(&timeinfo)) {
//     Serial.println("❌ Không lấy được thời gian!");
//     return;
//   }
//   pinMode(2, OUTPUT);
//   digitalWrite(2, HIGH);
//   // Cấu hình Firebase
//   config.host = FIREBASE_HOST;
//   config.signer.tokens.legacy_token = FIREBASE_AUTH;
//   Firebase.begin(&config, &auth);
//   Firebase.reconnectWiFi(true);
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------
//   particleSensor.setup();
//   particleSensor.setPulseAmplitudeRed(0x0A); // bật LED đỏ
//   particleSensor.setPulseAmplitudeIR(0x0A);  // bật LED IR
//   particleSensor.setPulseAmplitudeGreen(0);  // tắt LED xanh
// }

// void loop() 
// {
//   raw_data raw_data_1;
//   Electrocardiogram Electrocardiogram_1;
//   raw_data_1.irValue = particleSensor.getIR();
//   raw_data_1.redValue = particleSensor.getRed();

//   // // // ----- Tính SpO2 theo thuật toán đơn giản -----
//   float ratio = (float)raw_data_1.redValue / (float)raw_data_1.irValue;
//   Electrocardiogram_1.SpO2 = 110.0 - 25.0 * ratio;

//   // ----- Phát hiện nhịp tim -----
//   if (checkForBeat(raw_data_1.irValue)) 
//   {
//     long delta = millis() - lastBeat;
//     lastBeat = millis();
//     Electrocardiogram_1.beatsPerMinute = 60 / (delta / 1000.0);

//     if (Electrocardiogram_1.beatsPerMinute < 255 && Electrocardiogram_1.beatsPerMinute > 20) 
//     {
//       rates[rateSpot++] = (byte)Electrocardiogram_1.beatsPerMinute;
//       rateSpot %= RATE_SIZE;

//       Electrocardiogram_1.beatAvg = 0;
//       for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
//       Electrocardiogram_1.beatAvg /= RATE_SIZE;
      
//     }
//       // // ----- Tính SpO2 theo thuật toán đơn giản ----- void loop() 
// {
//   raw_data raw_data_1;
//   Electrocardiogram Electrocardiogram_1;
//   raw_data_1.irValue = particleSensor.getIR();
//   raw_data_1.redValue = particleSensor.getRed();

//   // // // ----- Tính SpO2 theo thuật toán đơn giản -----
//   float ratio = (float)raw_data_1.redValue / (float)raw_data_1.irValue;
//   Electrocardiogram_1.SpO2 = 110.0 - 25.0 * ratio;

//   // ----- Phát hiện nhịp tim -----
//   if (checkForBeat(raw_data_1.irValue)) 
//   {
//     long delta = millis() - lastBeat;
//     lastBeat = millis();
//     Electrocardiogram_1.beatsPerMinute = 60 / (delta / 1000.0);

//     if (Electrocardiogram_1.beatsPerMinute < 255 && Electrocardiogram_1.beatsPerMinute > 20) 
//     {
//       rates[rateSpot++] = (byte)Electrocardiogram_1.beatsPerMinute;
//       rateSpot %= RATE_SIZE;

//       Electrocardiogram_1.beatAvg = 0;
//       for (byte x = 0; x < RATE_SIZE; x++) beatAvg += rates[x];
//       Electrocardiogram_1.beatAvg /= RATE_SIZE;
      
//     }
//       // // ----- Tính SpO2 theo thuật toán đơn giản -----
//   }
//   if(raw_data_1.irValue<10000)
//   {
//     Electrocardiogram_1.SpO2 = 0;
//   }
  
//   }
//   if(raw_data_1.irValue<10000)
//   {
//     Electrocardiogram_1.SpO2 = 0;
//   }
  
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------


// //----------------------------------------------------------------
// int so_adc = 150;
// char chuoi[700] = ""; 
// // Lặp đo ADC và ghi kèm thời gian
// for (int i = 0; i < so_adc; i++) 
// {
//   if (digitalRead(32) == 0 && digitalRead(35) == 0)
//   { 
//     raw_data_1.adcValue = analogRead(34);
//     float voltage = ((float)raw_data_1.adcValue / 4095.0) * 3300.0;
//     char volt[10];
//     sprintf(volt, "-%.0f", voltage);  // Ví dụ: "-123.45"
//     strcat(chuoi, volt);
//     // delay(5);
//   }
// }


// //----------------------------------------------------------------
//     // Tạo chuỗi thời gian
//     // char datetime[900];
//     struct tm timeinfo;
//     // if (getLocalTime(&timeinfo)) 
//     // {
//               // sprintf(datetime, "%04d/%02d/%02d/%02d/%02d/%02d",
//               // timeinfo.tm_year + 1900,
//               // timeinfo.tm_mon + 1,
//               // timeinfo.tm_mday,
//               // timeinfo.tm_hour,
//               // timeinfo.tm_min,
//               // timeinfo.tm_sec);

//       // Ghép chuỗi cuối cùng: volt + datetime + xuống dòng
//       // strcat(datetime,chuoi);
//     // }

// //----------------------------------------------------------------


// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// //----------------------------------------------------------------
// uint64_t now = esp_timer_get_time();
// if (now - lastMicros >= intervalMicros) 
// {
//   if (timeinfo.tm_year + 1900 >= 2025)
//   {
//     char pathBuffer[64];  // Dùng chung cho tất cả đường dẫn, tiết kiệm bộ nhớ

//     // 1. ECG
//     sprintf(pathBuffer, "/ECG/%04d/%02d/%02d/%02d/%02d/%02d",
//             timeinfo.tm_year + 1900,
//             timeinfo.tm_mon + 1,
//             timeinfo.tm_mday,
//             timeinfo.tm_hour,
//             timeinfo.tm_min,
//             timeinfo.tm_sec);
//     Firebase.setString(fbdo, pathBuffer, chuoi);

//     // 2. BPM
//     sprintf(pathBuffer, "/BPM/%04d/%02d/%02d/%02d/%02d/%02d",
//             timeinfo.tm_year + 1900,
//             timeinfo.tm_mon + 1,
//             timeinfo.tm_mday,
//             timeinfo.tm_hour,
//             timeinfo.tm_min,
//             timeinfo.tm_sec);
//     Firebase.setInt(fbdo, pathBuffer, Electrocardiogram_1.beatAvg);

//     // 3. SpO2
//     sprintf(pathBuffer, "/SpO2/%04d/%02d/%02d/%02d/%02d/%02d",
//             timeinfo.tm_year + 1900,
//             timeinfo.tm_mon + 1,
//             timeinfo.tm_mday,
//             timeinfo.tm_hour,
//             timeinfo.tm_min,
//             timeinfo.tm_sec);
//     Firebase.setInt(fbdo, pathBuffer, Electrocardiogram_1.SpO2);

//     // Cập nhật mốc thời gian
//     lastMicros = now;
//   }
// }

// //-----------------------------------------------------------

//   // ----- In kết quả -----
//   Serial.print("IR="); // phát hiện có tay hay ko
//   Serial.print(raw_data_1.irValue);
//   // Serial.print(", RED=");
//   // Serial.print(redValue);
//   Serial.print(", BPM=");
//   Serial.print(Electrocardiogram_1.beatsPerMinute);
//   Serial.print(", Avg BPM=");
//   Serial.print(Electrocardiogram_1.beatAvg);
//   Serial.print(", ADC=");
//   Serial.print(raw_data_1.adcValue);
//   Serial.print("mV");
//   // Serial.print("ngay =");
//   // Serial.print(pathBuffer);
//   Serial.print("chuoi=");
//   Serial.print(chuoi);
//   Serial.print(", SpO2=");
//   Serial.print(Electrocardiogram_1.SpO2);
//   Serial.println(" %");

//   delay(10);
// }
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"
#include <Arduino.h>
#include <WiFi.h>
#include <FirebaseESP32.h>
#include <WiFiClient.h>
#include <time.h>

#define FIREBASE_HOST "https://esp32-9c871-default-rtdb.firebaseio.com/"
#define FIREBASE_AUTH "AIzaSyDneFPslsW4O0-3TGLV5yAWFvGaRbdttuY"

const long  gmtOffset_sec = 7 * 3600;
const int   daylightOffset_sec = 0;
const char* ssid = "TuNaTech 2.4G";
const char* password = "123456789";

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

MAX30105 particleSensor;

const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;

float beatsPerMinute;
int beatAvg;

uint64_t lastMicros = 0;
const uint64_t intervalMicros = 5000000;

struct Electrocardiogram {
  float SpO2;
  float beatsPerMinute;
  int beatAvg;
};

struct raw_data {
  int irValue;
  int redValue;
  int adcValue;
};


void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("Khong tim thay cam bien MAX30105.");
    while (1);
  }

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  configTime(gmtOffset_sec, daylightOffset_sec, "pool.ntp.org");
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo)) {
    Serial.println("❌ Khong lay duoc thoi gian!");
    return;
  }

  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH);

  config.host = FIREBASE_HOST;
  config.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeIR(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
}

void loop() {
  raw_data raw;
  Electrocardiogram ecg;
  struct tm timeinfo;

  raw.irValue = particleSensor.getIR();
  raw.redValue = particleSensor.getRed();

  float ratio = (float)raw.redValue / (float)raw.irValue;
  // ecg.SpO2 = raw.irValue < 10000 ? 0 : 110.0 - 25.0 * ratio;
  ecg.SpO2 = 110.0 - 25.0 * ratio;

  if (checkForBeat(raw.irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();
    ecg.beatsPerMinute = 60 / (delta / 1000.0);

    if (ecg.beatsPerMinute > 20 && ecg.beatsPerMinute < 255) {
      rates[rateSpot++] = (byte)ecg.beatsPerMinute;
      rateSpot %= RATE_SIZE;
      int sum = 0;
      for (byte x = 0; x < RATE_SIZE; x++) sum += rates[x];
      ecg.beatAvg /= RATE_SIZE;
    }
  }

  const int so_adc = 500;
  char chuoi[2000] = "";
  for (int i = 0; i < so_adc; i++) {
    if (digitalRead(32) == 0 && digitalRead(35) == 0) {
      raw.adcValue = analogRead(34);
      float voltage = ((float)raw.adcValue / 4095.0) * 3300.0;
      char volt[10];
      sprintf(volt, "-%.0f", voltage);
      strcat(chuoi, volt);
      delay(5);
    }
  }

  uint64_t now = esp_timer_get_time();
  // if (now - lastMicros >= intervalMicros) {
    if (getLocalTime(&timeinfo) && timeinfo.tm_year + 1900 >= 2025) {
      char pathBuffer[64];

      sprintf(pathBuffer, "/ECG/%04d/%02d/%02d/%02d/%02d/%02d",
              timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
              timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
      Firebase.setString(fbdo, pathBuffer, chuoi);

      sprintf(pathBuffer, "/BPM/%04d/%02d/%02d/%02d/%02d/%02d",
              timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
              timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
      Firebase.setInt(fbdo, pathBuffer, ecg.beatAvg);

      sprintf(pathBuffer, "/SpO2/%04d/%02d/%02d/%02d/%02d/%02d",
              timeinfo.tm_year + 1900, timeinfo.tm_mon + 1, timeinfo.tm_mday,
              timeinfo.tm_hour, timeinfo.tm_min, timeinfo.tm_sec);
      Firebase.setInt(fbdo, pathBuffer, ecg.SpO2);

      lastMicros = now;
    }
  // }

  Serial.print("IR="); Serial.print(raw.irValue);
  Serial.print(", BPM="); Serial.print(ecg.beatsPerMinute);
  Serial.print(", Avg BPM="); Serial.print(ecg.beatAvg);
  Serial.print(", ADC="); Serial.print(raw.adcValue); Serial.print("mV");
  Serial.print(", SpO2="); Serial.print(ecg.SpO2); Serial.print(" %");
  Serial.print(", chuoi="); Serial.println(chuoi);

  delay(10);
}