#include <ArduinoBLE.h>
#include <Arduino_APDS9960.h>
#include "Arduino_BMI270_BMM150.h"

BLEService customService("180C");
BLEStringCharacteristic ble_sensor("2A56", BLERead |BLENotify, 40);


float aX,aY,aZ, gX, gY, gZ;
String data;
void setup() {
  Serial.begin(9600);
  while (!Serial);
  
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
  if (!BLE.begin()) {
    Serial.println("* Starting Bluetooth® Low Energy module failed!");
    while (1);
  }
  
  BLE.setLocalName("Arduino Datanauts"); 
  BLE.setAdvertisedService(customService);
  customService.addCharacteristic(ble_sensor);

  BLE.addService(customService);
  

  BLE.advertise();

  Serial.println("Arduino Datanauts");
  Serial.println(" ");
}


void loop() {
    BLEDevice central = BLE.central(); // wait until central conects
    if ( central )
  {
    Serial.print( "Connected to central: " );
    Serial.println( central.address() );

    while (central.connected()) {

        if (IMU.gyroscopeAvailable() && IMU.accelerationAvailable()){
          IMU.readGyroscope(gX,gY,gZ);
          IMU.readAcceleration(aX,aY,aZ);
          //data = String(aX) + "," + String(aY) + ","+  String(aZ)+String(aX) + "," + String(aY) + ","+  String(aZ);
          data = String(aX) + "," + String(aY) + ","+  String(aZ) +","+ String(gX) + "," + String(gY) + ","+  String(gZ);
          // print the data 
          Serial.print(aX, 3);
          Serial.print(',');
          Serial.print(aY, 3);
          Serial.print(',');
          Serial.print(aZ, 3);
          Serial.print(',');
          Serial.print(gX, 3);
          Serial.print(',');
          Serial.print(gY, 3);
          Serial.print(',');
          Serial.print(gZ, 3);
          Serial.println();

          ble_sensor.writeValue(data.c_str()); //sends data
          }
      //delay(100); //should def. check  
    }
  }
  Serial.print( "Disconnected from central: " );
  Serial.println( central.address() );
}