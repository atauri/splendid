/*
recive en mensaje ESP_now, y lo inserta por MQTT
con los comandos AT del modem

formato del mensaje MQTT para insertar en el servidor
AT+MPUB="splendid/insert/temp",2,0,"23.2_{mac_modem}_{mac sensor}_2500"

*/
#include <WiFi.h>
#include "esp_now.h"


// ESP_NOW ====================================
struct Data {
    float temp;
    char mac[18];
    int bat;    
} myData;

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

// ESPN OW callback function that will be executed when data is received
void OnDataRecv(const esp_now_recv_info_t *mac, const uint8_t *incomingData, int len) {

  memcpy(&myData, incomingData, len);
  Serial.println(myData.temp);
  Serial.println(myData.mac);
  Serial.println(myData.bat);
  insertar(String(myData.temp), String(myData.mac), String(myData.bat)); 
}


HardwareSerial MySerial(0); // UART para el modem

// publicar mensage MQTT
void insertar(String tempString, String mac, String bat){
  
  String msg = tempString+"_"+ WiFi.macAddress()+"_"+mac+"_"+bat;
  Serial.println(msg);
  Serial.println("_____________________");

  MySerial.print("AT+MPUB=\"splendid/insert/temp\",2,0,\""+msg+"\"\r\n");
  delay(1000);
  leerSerial();
}


void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  // initialize both serial ports:
  Serial.begin(115200);
  MySerial.begin(115200); // at CPU Freq is 40MHz, work half speed of defined.
  delay(500);
  beginEspNow(); 
}

bool checkMqtt(){

    String s = "";
    MySerial.print("AT+MQTTSTATU\r\n");
    delay(500);
    s=leerSerial();
    //Serial.println(s);
    if (s.indexOf(":1")>-1){
      Serial.println("MQTT ok");
      digitalWrite(LED_BUILTIN,HIGH);
      return true;
    }
    digitalWrite(LED_BUILTIN, LOW);
    Serial.println("MQTT NO CONCTADO :-(");
    return false;
}

void conectarMqtt(){
     
    MySerial.print("AT+MCONFIG=\"modem1\",\"tadu\",\"sogtulakk\"\r\n");
    delay(500);
    Serial.println(leerSerial());
    MySerial.print("AT+MIPSTART=\"titi.etsii.urjc.es\",\"60000\"\r\n");
    delay(500);
    Serial.println(leerSerial());
    MySerial.print("AT+MCONNECT=1,3600\r\n");
    delay(500);
    Serial.println(leerSerial());
}

bool checkRed(){
  
    //AT+CGATT? 
    // 1 connectado 0, no conectdo
    MySerial.print("AT+CGATT?\r\n");
    delay(500);
    String s = leerSerial();
    //Serial.println(s);
    if (s.indexOf("1")>-1){
      Serial.println("RED ok");
      digitalWrite(LED_BUILTIN, HIGH);
      return true;
    }
    digitalWrite(LED_BUILTIN, LOW);
    return(false);
}

String leerSerial(){
  
  String s= "";
  while(MySerial.available()) { 
    s += MySerial.readString();
  }
  return s;
}

void loop() {
  

    int i=0;
    while (!checkRed()){
      delay(1000);
      if (i>60) {
        MySerial.print("AT+RESET\r\n");
      }else{
        i+=1;
        Serial.println(i);
      }
      
    };
    if (!checkMqtt()) conectarMqtt();
    delay(5000);
}