/*
formato temperatura para insertar en el servidor
AT+MPUB="splendid/insert/temp",2,0,"23.2"

*/
#include <WiFi.h>
#include "esp_now.h"
//#include <esp_wifi.h>


// MQTT ====================================

//#include <PubSubClient.h>

// WiFi
/*
const char *ssid = "apilink"; // Enter your WiFi name
const char *password = "qwerty20";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "titi.etsii.urjc.es";
const char *topic = "splendid/insert/temp";
const char *mqtt_username = "tadu";
const char *mqtt_password = "sogtulakk";
const int mqtt_port = 60000;

WiFiClient espClient;
PubSubClient client(espClient);*/

// ESP_NOW ====================================

struct Data {
    float temp;
    char mac[18];
    int bat;    
} myData;
String myMac = "";

// ESPN OW callback function that will be executed when data is received
// Init ESP-NOW ---------------------------------------------------------------
void beginEspNow(){

  WiFi.mode(WIFI_AP_STA);
  myMac = WiFi.macAddress();
  Serial.println(myMac);
  
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(OnDataRecv);
  Serial.println("\nesp now listo");
  
}

//void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
void OnDataRecv(const esp_now_recv_info_t *mac, const uint8_t *incomingData, int len) {

  memcpy(&myData, incomingData, len);
  Serial.println(myData.temp);
  Serial.println(myData.mac);
  Serial.println(myData.bat);

  // meterle la mac del gateway
  String macs = myMac+"_"+String(myData.mac);
  insertar(String(myData.temp), macs , String(myData.bat)); 
}


HardwareSerial MySerial(0); // UART para el el otro esp que inserta por wifi

// publicar mensage MQTT
void insertar(String tempString, String mac, String bat){
  
  String msg=tempString+"_"+mac+"_"+bat;
 
  //Serial.print("AT+MPUB=\"splendid/insert/temp\",2,0,\""+msg+"\"\r\n");
  Serial.print("splendid/insert/temp,"+msg+"\r\n");
  // se lo envío al otro esp para que lo publiquye por la wifi
  MySerial.println("splendid/insert/temp,"+msg);
  
  /*
  MySerial.print("AT+MCONFIG=\"mac\",\"tadu\",\"sogtulakk\"\r\n");
  delay(1000);
  leerSerial();
  
  MySerial.print("AT+MIPSTART=\"titi.etsii.urjc.es\",\"60000\"\r\n");
  delay(1000);
  leerSerial();
  
  MySerial.print("AT+MCONNECT=1,60\r\n");
  delay(1000);
  leerSerial();

  // AT+MPUB="splendid/insert/temp",2,0, "20.6"

  MySerial.print("AT+MPUB=\"splendid/insert/temp\",2,0,\""+msg+"\"\r\n");
  delay(1000);
  leerSerial();
  */
}


void setup() {
  // initialize both serial ports:
  Serial.begin(115200);
  MySerial.begin(115200); // at CPU Freq is 40MHz, work half speed of defined.
  delay(500);
  Serial.println("(A) Hola");
  //MySerial.println("(A) Hola");
  beginEspNow();
  
  //WiFi.mode(WIFI_STA);
  
  
  /*WiFi.begin(ssid, password); //check wi-fi is connected to wi-fi network
  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
  Serial.println("wifi connected");
    */
  //esp_wifi_set_channel(0x01, WIFI_SECOND_CHAN_NONE);
  /*if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  Serial.println("esp ok");
  esp_now_register_recv_cb(OnDataRecv);*/
  //client.setServer(mqtt_broker, mqtt_port);
  //client.setCallback(callback);
  
  /*while (!client.connected()) {
      String client_id = "esp32-client-";
      client_id += String(WiFi.macAddress());
      Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
      if (client.connect(client_id.c_str(), mqtt_username, mqtt_password)) {
          Serial.println("Public EMQX MQTT broker connected");
      } else {
          Serial.print("failed with state ");
          Serial.print(client.state());
          delay(2000);
      }
  }*/
}

void leerSerial(){

  while(MySerial.available()) { 
    Serial.print(MySerial.readString());
  }

}

void loop() {

  //client.loop();
}