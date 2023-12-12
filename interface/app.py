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


class unatest(toga.App):

    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))

        
        
        button = toga.Button(
            "Say Hello!",
            on_press=self.say_hello,
            style=Pack(padding=5)
        )


       
        main_box.add(button)
        
        self.show_label = toga.Label("Values:")
        main_box.add(self.show_label)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    async def say_hello(self, widget):
        widget.text = "scanning"
        device_found = None
        scanned = await bleak.BleakScanner.discover()
        for device in scanned:
            if device.name == "Arduino Datanauts":
                widget.text = device.name
                device_found = device


        async with bleak.BleakClient(device_found.address) as client:
            await client.start_notify("00002A56-0000-1000-8000-00805f9b34fb", self.handle_notification)
            widget.text = "connected"
            await client.stop_notify("00002A56-0000-1000-8000-00805f9b34fb")
        widget.text = "disconnected"
        self.show_label.text += "read values"



    def handle_notification(self, sender:str, data:bytearray): 
        data_read = data.decode()
        name_file = "appa_data"+".csv"
        self.show_label.text = data_read

def main():
    return unatest()
