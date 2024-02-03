#include <ArduinoBLE.h>
#include <Arduino_APDS9960.h>
#include "Arduino_BMI270_BMM150.h"

#include <TensorFlowLite.h>
#include <tensorflow/lite/micro/all_ops_resolver.h>
#include <tensorflow/lite/micro/micro_interpreter.h>
#include <tensorflow/lite/schema/schema_generated.h>

#include "model.h"

// Sets up bluetooth requirements
BLEService customService("180C");
BLEStringCharacteristic ble_sensor("2A56", BLERead |BLENotify, 40);
BLEStringCharacteristic fall_sensor("2A50",BLERead |BLENotify,20);
BLEStringCharacteristic battery_sensor("2A55",BLERead |BLENotify,20);

// Sets up TFLM ops
tflite::AllOpsResolver tflOpsResolver;
const tflite::Model* tflModel = nullptr;
tflite::MicroInterpreter* tflInterpreter = nullptr;
TfLiteTensor* tflInputTensor = nullptr;
TfLiteTensor* tflOutputTensor = nullptr;

// Create a static memory buffer for TFLM
constexpr int tensorArenaSize = 32 * 1024;
byte tensorArena[tensorArenaSize] __attribute__((aligned(16)));

// Global variables
float aX, aY, aZ;
const float accelerationThreshold = 0.28; // threshold of significant in G's
int samplesRead = 200;
String data, data_fall;

// array to map indices to a name
const char* Activites[] = 
{
  "FALL",
  "ADL"
};

void setup() 
{
  Serial.begin(9600);
  
  if (!IMU.begin()) 
  {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  if (!BLE.begin()) 
  {
    Serial.println("*Starting Bluetooth® Low Energy module failed!");
    while (1);
  }
  
  // Set bluetooth connection settings
  BLE.setLocalName("Arduino Datanauts"); 
  BLE.setAdvertisedService(customService);
  customService.addCharacteristic(ble_sensor);
  customService.addCharacteristic(fall_sensor);
  customService.addCharacteristic(battery_sensor);

  BLE.addService(customService);
  BLE.advertise();

  // get the TFL representation of the model byte array
  tflModel = tflite::GetModel(model);
  if (tflModel->version() != TFLITE_SCHEMA_VERSION) 
  {
    Serial.println("Model schema mismatch!");
    while (1);
  }

  // Create an interpreter to run the model
  tflInterpreter = new tflite::MicroInterpreter(tflModel, tflOpsResolver, tensorArena, tensorArenaSize);
  // Allocate memory for the model's input and output tensors
  tflInterpreter->AllocateTensors();
  // Get pointers for the model's input and output tensors
  tflInputTensor = tflInterpreter->input(0);
  tflOutputTensor = tflInterpreter->output(0);  
}

/*
 * Checks availability of acceleration data and stores them if it is the case.
 */
bool readAccelerator()
{
  if (IMU.accelerationAvailable())
  {
    IMU.readAcceleration(aX,aY,aZ);
    return true;
  }
  return false;
}

/*
 * Normalize IMU data between 0 to 1 and store in the model's input tensor.
 */
bool addInputTensor()
{
  tflInputTensor->data.f[samplesRead * 3 + 0] = (aX + 1.93) / (1.97 +1.93);
  tflInputTensor->data.f[samplesRead * 3 + 1] = (aY + 1.94) / (1.99 +1.94);
  tflInputTensor->data.f[samplesRead * 3 + 2] = (aZ + 1.87) / (1.99 +1.87);
}

/*
 * Resets samples when motion already detected.
 */
void resetMotion()
{
  if (samplesRead == 200) 
  {
    if (readAccelerator()) 
    {
      float aSum = fabs(aX) + fabs(aY) + fabs(aZ);

      // Checks if acceleration sum is above the threshold
      if (aSum >= accelerationThreshold) 
      {
        // Resets sample read count
        samplesRead = 0;
      }
    }
  }
}

/*
 * Checks prediction and decides if a fall was detected.
 */
String detectFall()
{
  float fall = tflOutputTensor->data.f[0];
  float adl = tflOutputTensor->data.f[1];

  Serial.print(Activites[0]);
  Serial.print(": ");
  Serial.println(fall, 3);
  Serial.print(Activites[1]);
  Serial.print(": ");
  Serial.println(adl, 3);
 
  if (fall >= 0.6)
  {
    return "1";
  }
  return "0";
}

void loop() 
{
  BLEDevice central = BLE.central(); // Wait for established central connection
  if (central)
  {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) 
    {
      resetMotion();

      // Check availability of required samples
      if (samplesRead < 200) 
      {
        if (readAccelerator()) 
        { 
          data = String(aX) + "," + String(aY) + ","+  String(aZ);
          ble_sensor.writeValue(data.c_str());  // Sends accelerations

          addInputTensor();
       
          samplesRead++;

          if (samplesRead == 200) 
          {
            // Run inference
            
            TfLiteStatus invokeStatus = tflInterpreter->Invoke();

            if (invokeStatus != kTfLiteOk) 
            {
              Serial.println("Invoke failed!");
              while (1);
              return;
            }
            data_fall = detectFall();
            fall_sensor.writeValue(data_fall.c_str());  // Sends fall prediction
          }
          
        }
      }  
    }
  }
  Serial.print("Disconnected from central: ");
  Serial.println(central.address());
}