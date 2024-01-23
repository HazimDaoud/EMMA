#include <ArduinoBLE.h>
#include <Arduino_APDS9960.h>
#include "Arduino_BMI270_BMM150.h"

BLEService customService("180C");
BLEStringCharacteristic ble_sensor("2A56", BLERead |BLENotify, 40);

BLEStringCharacteristic fall_sensor("2A50",BLERead |BLENotify,20);
BLEStringCharacteristic battery_sensor("2A55",BLERead |BLENotify,20);


float aX,aY,aZ, gX, gY, gZ;
String data, data_fall, data_battery;
void setup() {
  Serial.begin(9600);
  //while (!Serial);
  
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
  customService.addCharacteristic(fall_sensor);
  customService.addCharacteristic(battery_sensor);

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
          

          ble_sensor.writeValue(data.c_str()); //sends data
          data_fall = String(0);
          if(aX*aX+aY*aY+aZ*aZ>2){
            data_fall = String(1);
          }
          fall_sensor.writeValue(data_fall.c_str());//here goes with get_prediction()

          
          Serial.print(',');
          Serial.print(69, 3);
          data_battery = String(69);// here goes the get_battery()
          battery_sensor.writeValue(data_battery.c_str());
          Serial.println();
          }
      //delay(1000); //should def. check  
    }
  }
  Serial.print( "Disconnected from central: " );
  Serial.println( central.address() );
}