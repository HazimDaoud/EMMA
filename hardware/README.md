# Hardware Folder
This folder contains the hardware-related components for the Fall Detection project. 

## Overview

In this project we work with the Arduino Nano BLE Sense Rev2. The folder contains an .ino script which reads sensor data via bluetooth. The python script then saves them in a csv file in order to evaluate them in a python model.
It also contains an .ino code which runs an inference on a trained model with real-time data to calculate a fall prediction based on our collected data.

## Folder Structure

Describe the organization of the project files within the folder.

- `/sample_data_arduino.ino`: Contains the Arduino code for reading sensor data and sending it via bluetooth to our connected python code.
- `/sample_data_ble.py`: Includes Python script responsible for connecting via bluetooth to the Arduino Nano BLE Sense Rev2 and saving sensor data in a csv file.
- `/tflite_ble_transfer.ino`: Stores a trained model, runs inference on the model with real-time measured data and calculate a prediction about the detected fall. Afterwards sending the data via bluetooth to the python interface.

## Troubleshooting

Moving tflite modules in different orders or out of void loops() can cause unpredictable errors during runtime and might block uploads on arduino.
