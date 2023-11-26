import asyncio
import aioconsole
import os
from bleak import BleakClient
from bleak import discover
import sys

# my global variables
label = "normal"
label_index = "0"
recording = True

def change_label(new_label = label,repeat = False):
    global label
    global label_index
    label = new_label
    new_index = 0

    try: #update index value if we already have measurments with the same lable 
        new_index = [f for f in os.listdir(os.getcwd()) if label in f]
        new_index.sort(key=lambda f: int(''.join(filter(str.isdigit, f)))) # sort it with number order
        new_index = new_index[-1]
        new_index = int(new_index.split("_")[-1].split(".")[0])
      
        if not repeat: # if want to redo the last measurment
            new_index += 1
        
    except:
        new_index = "0"  

    label_index = str(new_index) #updates value

def handle_notification(sender, data): 
    data_read = data.decode()
    name_file = label+"_"+ label_index+".csv"

    with open(name_file,'a') as f: #reads incoming data and stores it in a separatly file
        f.write(data_read)
        f.write("\n")


async def scan_near(): #could end up changing later for automatic detection of device
    found = False
    scanned = await discover()

    for device in scanned:
        if 'Arduino Datanauts' in device.name:
            print('Found Arduino Datanauts device')
            found = True
    if found:
        asyncio.sleep(10000)
    else:
        asyncio.sleep(10)


async def read_comms(comm):
    match comm:
        case "change":
            new_label = await aioconsole.ainput('Enter new label \n')
            change_label(new_label=new_label)
        case "redo":
            change_label(new_label = label,repeat = True) #overwrites the last measurment
        case "new":
            print(label)
            change_label(new_label = label) #uses last label when no new label is given
           
        case "exit":
            print('Exiting programm... \n')
            sys.exit()
        case "help":
            comm = await aioconsole.ainput('Commands: \n new : to take a new measurment from the same label class as the last one (normal as default) \n redo: to overwrite the last measurment \n change: to change the lable of the measurment (then insert the desired label) \n exit: exits the program \n')
            await read_comms(comm)
        case _:
            comm = await aioconsole.ainput('Unknown command (try: new, redo, change, exit, help)) \n')
            await read_comms(comm)

            


async def read_BLE(address, loop):
    print("Connecting...")
    async with BleakClient(address, loop=loop) as client:
        print("Connected")
        while True:
            comm =  await aioconsole.ainput('Start measurment, type new to use the previous label, default is normal or type change to set a different label)\n') #waits until event is set to record data
            
            await read_comms(comm)
                    
            # Start receiving notifications for the accelerometer data
            await client.start_notify("00002A56-0000-1000-8000-00805f9b34fb", handle_notification)
            # Keep recording until given so 
            comm = await aioconsole.ainput('Press Enter to stop measurment')

            await client.stop_notify("00002A56-0000-1000-8000-00805f9b34fb")
            
            

# Address of the BLE peripheral to connect to
address = "C5:63:C2:5A:5F:89"
 
# Get the event loop
loop = asyncio.get_event_loop()
#run async function
loop.run_until_complete(read_BLE(address, loop))


