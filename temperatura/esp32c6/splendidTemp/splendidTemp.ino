/*
Lee la temeratura (ds18b20) cada media hora,
la envía por esp-now a CUALQUIERA que esté escuchando
  - temperatura
  - Mac Address
  - nivel de batería
y se duerme (deepSleep)

Para DFRobot Beetle ESP32-C6 (con batería lipo 800 mAmp soldada)

*/



#include "myDs18b20.h"
#include "esp_now.h"
#include <WiFi.h>
#define uS_TO_S_FACTOR 1000000//ULL /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  1800 //3600         /* Time ESP32 will go to sleep (in seconds) */

//#define placa "XIAO"
#define placa "dfRobot"
//#define placa "mini"



//A TODOS, CUALQUIERA QUE ESTÉ ESCUCHANDO
uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}; 

const int ledPin = 15; // dfRobot esp32 c6 mini

typedef struct struct_message {
    float temp;
    char mac[18];
    int bat;
} struct_message;

// Create a struct_message called myData
struct_message myData;
esp_now_peer_info_t peerInfo;

// callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
  if (placa == " XIAO") delay(1000);
  dormir();  
}
//lee la bateria (Solo DFRobot)
int bat(){
  int analogValue = analogRead(0);
  int analogVolts = analogReadMilliVolts(0);

  Serial.print(analogVolts * 2);
  Serial.println("mV");
  return analogVolts * 2;
}

void dormir(){

    // DFROBOT -> leer https://community.dfrobot.com/makelog-314135.html
    // Duerme si NO hay puerto serie
    if (!Serial){
          if (placa == "XIAO") digitalWrite(LED_BUILTIN, LOW);
          //delay(1000);
          Serial.println("A dormir");
          delay(1000);
          analogWrite(ledPin, 0);
          //DEEP SLEEP
          esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
          esp_deep_sleep_start();
    
    }else{
      Serial.println("No puedo dormir");
      if (placa == "XIAO") digitalWrite(LED_BUILTIN, HIGH);
    }
}
void conectar(){
  Serial.println("conectar()");
  //WiFi.mode(WIFI_STA);

  // Init ESP-NOW
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  Serial.println("init ok");
  // Once ESPNow is successfully Init, we will register for Send CB to
  // get the status of Trasnmitted packet
  esp_now_register_send_cb(OnDataSent);
  Serial.println("callback ok");
  // Register peer
  memcpy(peerInfo.peer_addr, broadcastAddress, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;
  
  // Add peer        
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
  Serial.println("peer ok");
  
}
//==================================================
void setup() {

  Serial.begin(115200);
  delay(500);
  Serial.println("Hola!");
  
  // In it Serial Monitor
  if(Serial){
    if (placa == "XIAO") digitalWrite(LED_BUILTIN, LOW);
    else analogWrite(ledPin, 0); // apaga el led de la placa
    bat();
  }else{
    if (placa == "XIAO") {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(1000);}
    else analogWrite(ledPin, 255); // enciende el led 
  };
  
  // get MAC address
  WiFi.mode(WIFI_STA);
  String m = WiFi.macAddress();
  m.toCharArray(myData.mac, 18); //
  Serial.println( myData.mac);
  Serial.println("-------------------------");

  conectar();
  
  //init temp sensor
  beginDs18b20();
  leer();
  esp_err_t result = esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
  dormir();
}
 
void ledIn(){
  //LED fade in 
  for(int dutyCycle = 0; dutyCycle <= 255; dutyCycle++){   
    analogWrite(ledPin, dutyCycle);
    delay(15);
  }
}
void ledOut(){
  //LED fade off
  for(int dutyCycle = 255; dutyCycle >= 0; dutyCycle--){
    analogWrite(ledPin, dutyCycle);
    delay(15);
  }
}

void leer(){
  float t = leerDs18b20(); //random(1,100)/10.0;
  Serial.println(t);
  //Serial.println(myData.mac);
  myData.temp = t;
  myData.bat = bat();
}

void loop() {

  delay(10000);
  Serial.print(".");
  
}
