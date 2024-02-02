import argparse
import asyncio

import random
import numpy as np
import time

import bleak
from bleak import BleakScanner
from bleak import BleakClient



async def ble_connection():
    print("scanning")
    scanned = await bleak.BleakScanner.discover()
    device_list = []
    for device in scanned:
        if  device.name == "Arduino Datanauts" :
            device_list = device
    
    
    print('connectiong...')
    async with bleak.BleakClient(device_list.address) as client:
        connected = True #once its connected
        
        await client.start_notify("00002A56-0000-1000-8000-00805f9b34fb", handle_notification)
        await client.start_notify("00002A50-0000-1000-8000-00805f9b34fb", handle_notification_fall)
        ##await client.start_notify("00002A55-0000-1000-8000-00805f9b34fb", handle_notification_battery)
        while True: # currently hears what arduino is sending
            await asyncio.sleep(1) #could change frequency of readings 
        await client.stop_notify("00002A56-0000-1000-8000-00805f9b34fb")
        await client.stop_notify("00002A50-0000-1000-8000-00805f9b34fb")
        #await client.stop_notify("00002A55-0000-1000-8000-00805f9b34fb")

def handle_notification_fall(sender:str, data:bytearray):
    data_read = data.decode()
    data_read = int(data_read)
    if data_read:
        print('Fall')
    else:
        print('ADL')

def handle_notification(sender:str, data:bytearray):
    
    data_read = data.decode()
    data_read = np.fromstring(data_read, dtype=float, sep=',') #incoming data as an array


# Get the event loop
loop = asyncio.get_event_loop()
#run async function
loop.run_until_complete(ble_connection())     