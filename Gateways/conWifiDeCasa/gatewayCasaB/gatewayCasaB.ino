/*
formato temperatura para insertar en el servidor
mensaje mqtt: "splendid/insert/temp,{float temperatua},{mac},{int Bateria}"
*/
#include <WiFi.h>

// MQTT ====================================

#include <PubSubClient.h>

// WiFi

const char *ssid = "apilink"; // Enter your WiFi name
const char *password = "qwerty20";  // Enter WiFi password

// MQTT Broker
const char *mqtt_broker = "titi.etsii.urjc.es";
const char *topic = "splendid/insert/temp";
const char *mqtt_username = "tadu";
const char *mqtt_password = "sogtulakk";
const int mqtt_port = 60000;

WiFiClient espClient;
PubSubClient client(espClient);

HardwareSerial MySerial(0); // UART para el el otro esp que inserta por wifi

// publicar mensage MQTT
void insertar(String msg){
  //msg = "splendid/insert/temp,2,0,13.69_F0:F5:BD:07:97:0C_4026";
  String topic = msg.substring(0, msg.indexOf(','));
  Serial.println(topic);
  String payload = msg.substring(msg.indexOf(',')+1,msg.length()-1);
  Serial.println(payload);
  Serial.println("================");
  client.publish(topic.c_str(), payload.c_str() );
}

// recibo si estoy suscrito a un topic
void callback(char* topic, byte* message, unsigned int length) {
  Serial.println("callback");
}

void setup() {

  // initialize both serial ports:
  Serial.begin(115200);
  MySerial.begin(115200); // at CPU Freq is 40MHz, work half speed of defined.
  delay(500);
  Serial.println("(B) Hola");

  // conectar a la wifi--------------

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password); //check wi-fi is connected to wi-fi network
  while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.print(".");
    }
  Serial.println("wifi connected");

  // conectar a mosquitto-----------------

  client.setServer(mqtt_broker, mqtt_port);
  client.setCallback(callback);
  
  while (!client.connected()) {
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
  }
}


void loop() {
 while(MySerial.available()) {
    String msg = MySerial.readString(); 
    Serial.print(msg);
    insertar(msg);
  }
}