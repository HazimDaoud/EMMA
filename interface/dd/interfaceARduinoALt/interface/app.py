"""
My first application
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import bleak
from bleak import BleakScanner
from bleak import BleakClient
import asyncio
import numpy as np




class unatest(toga.App):

    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))

        button_disconnect = toga.Button("Disconnect", on_press=self.disconnectBLE,style=Pack(padding=5))
        button_connect = toga.Button("Start Connection", on_press=self.connectBLE,style=Pack(padding=5))

        self.label_status = toga.Label("Device: None")
        self.label_connection = toga.Label("Currently Disconnected")
        main_box.add(self.label_connection)
        main_box.add(self.label_status)
        main_box.add(button_disconnect)
        main_box.add(button_connect)
        
        self.show_label = toga.Label("Values:")
        main_box.add(self.show_label)





        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        self.connected = False
        self.data = np.zeros((3,10))
        self.device = None
      
        

    async def connectBLE(self,widget):
            if not self.connected :
                widget.text = "Start Connection"
                await self.scanBLE() #founds the addres to connect
                
                async with bleak.BleakClient(self.device.address) as client:
                        self.connected = True
                        widget.text="Currently Connected"
                        self.label_connection.text ="Currently Connected"
                        await client.start_notify("00002A56-0000-1000-8000-00805f9b34fb", self.handle_notification)
                        while self.connected: # currently hears what arduino is sending
                            await asyncio.sleep(1) #could change frequency of readings 
                        await client.stop_notify("00002A56-0000-1000-8000-00805f9b34fb")
                        widget.text ="Re Connect"
            print(self.data) #just to get idea how the values are stored


    
    def disconnectBLE(self,widget): #jto stop the connection
        self.connected = False
        self.label_connection.text ="Currently Disconnected"
       
        

    async def scanBLE(self): #to find the addres of the arduino
        self.label_status.text ="Scanning"
        scanned = await bleak.BleakScanner.discover()
        for device in scanned:
            if device.name == "Arduino Datanauts":
                self.device = device
        self.label_status.text = "Device : " + self.device.name

        



    def handle_notification(self, sender:str, data:bytearray): 
        data_read = data.decode()           # incoming data as a string
        data = np.fromstring(data_read, dtype=float, sep=',') #incoming data as an array
        for i in range(3): #update 3 for the 6 after we send more data, need to change the dimension of self.data also
            self.data[i]=np.roll(self.data[i],-1)#shifts array one
            self.data[i][-1]= data[i]   #update last value

        self.show_label.text = data_read


def main():
    return unatest()
