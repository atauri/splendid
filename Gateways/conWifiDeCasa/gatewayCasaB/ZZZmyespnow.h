#include <WiFi.h>
//#include <esp_wifi.h>
#include "esp_now.h"

struct Data {
    float temp;
    char mac[18];
    int bat;    
} myData;


// ESPN OW callback function that will be executed when data is received
//void OnDataRecv(uint8_t * mac, uint8_t *incomingData, uint8_t len) {
void OnDataRecv(const esp_now_recv_info_t *mac, const uint8_t *incomingData, int len) {
  

  memcpy(&myData, incomingData, len);

  Serial.println(myData.temp);
  Serial.println(myData.mac);
  
}

// Init ESP-NOW ---------------------------------------------------------------
void beginEspNow(){

  WiFi.mode(WIFI_AP_STA);
  String myMac = WiFi.macAddress();
  Serial.println(myMac);
  
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(OnDataRecv);
  Serial.println("\nesp now listo");
  
}

