from flask import Flask, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import numpy as np
import time
from datetime import datetime
from flask_socketio import SocketIO
import bleak
from bleak import BleakScanner
from bleak import BleakClient
import asyncio

global connected 
global data_buffer
global classification
global battery_percentage
global device_name
global prev_classification
prev_classification = False
connected = False
data_buffer = [0,0,0]
classification = False
battery_percentage = 69
device_name = "None"


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)


@app.route('/')
def main():
    with app.app_context():
        db.create_all()
    patients = Patient.query.all()
    if not Patient.query.first():
        add_patient()
    return render_template('index.html', battery_percentage=0, loading=False, connected=None, patients=patients)


@app.route('/update_battery')
def get_battery_percentage():
    return jsonify({'percentage': get_battery(), 'loading': False})

@app.route('/update_device')
def get_device_name():
    return jsonify({'device':get_device()})

@app.route('/connect')
async def connect_disconnect():
    global connected

    if connected:
        set_battery(0)
        set_data([0,0,0])
        set_device("None")
        await asyncio.sleep(5)
        connected = False
        
    else:
        await ble_connection()
    #connected = not connected
    return jsonify({'connected':connected})

@app.route('/scan_BLE')
async def ble_connection():
    global connected
    connected = None
    device = await ble_scan()
    #await fall_ble()
    set_device(device=device.name)
    
    
    async with bleak.BleakClient(device.address) as client:
        connected = True #once its connected
        
        await client.start_notify("00002A56-0000-1000-8000-00805f9b34fb", handle_notification)
        await client.start_notify("00002A50-0000-1000-8000-00805f9b34fb", handle_notification_fall)
        ##await client.start_notify("00002A55-0000-1000-8000-00805f9b34fb", handle_notification_battery)
        while connected: # currently hears what arduino is sending
            await asyncio.sleep(1) #could change frequency of readings 
        await client.stop_notify("00002A56-0000-1000-8000-00805f9b34fb")
        await client.stop_notify("00002A50-0000-1000-8000-00805f9b34fb")
        #await client.stop_notify("00002A55-0000-1000-8000-00805f9b34fb")

    return jsonify({'connected':connected})

def handle_notification_battery(sender:str, data:bytearray):
    data_read = data.decode()
    data_read = int(data_read)
    set_battery(data_read)
    


def handle_notification_fall(sender:str, data:bytearray):
    data_read = data.decode()
    data_read = int(data_read)
    set_prediction(data_read)

def handle_notification(sender:str, data:bytearray):
    prev_data = get_data()
    data_read = data.decode()
    data_read = np.fromstring(data_read, dtype=float, sep=',') #incoming data as an array

    for i in range(3): #update 3 for the 6 after we send more data
        prev_data[i]= data_read[i]

    set_data(data=prev_data)

@app.post('/trigger_prediction/<int:prediction>')
def post_prediction(prediction):
    global classification
    classification = prediction
    return jsonify({'prediction':classification})

def get_prev_classification():
    global prev_classification
    return prev_classification

def set_prediction(prediction):
    global classification
    global prev_classification

    prev_classification = classification
    classification = prediction
    #return jsonify({"prediction":prediction})
def get_device():
    global device_name
    return device_name

def set_device(device):
    global device_name
    device_name = device
def get_predict():
    global classification
    return classification

def set_data(data):
    global data_buffer
    data_buffer = data

def get_data():
    global data_buffer
    return data_buffer

def set_battery(battery):
    global battery_percentage
    battery_percentage = battery

def get_battery():
    global battery_percentage
    return battery_percentage

   
async def ble_scan():
    scanned = await bleak.BleakScanner.discover()
    device_list = []
    for device in scanned:
        if  device.name == "Arduino Datanauts" :
            device_list = device
    
    return device_list

@app.route('/update_fall')
def prediction_status():
    return jsonify({'prediction': get_predict()})



@app.route('/update_led')
def get_connection_status():
    global connected
    return jsonify({'connected': connected})


### Database Start ###
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    falls = db.relationship('Fall', backref='patient', lazy=True)


class Fall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now().replace(microsecond=0))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)


@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = "Ayman Kabawa"  # request.form.get('name')
    patient = Patient(name=name)
    db.session.add(patient)
    db.session.commit()
    return redirect(url_for('main'))


@app.route('/add_fall/<int:patient_id>', methods=['POST'])
def add_fall(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    fall = Fall(patient=patient)
    db.session.add(fall)
    db.session.commit()
    return jsonify({'dummy': 'This is a dummy return'})  # return redirect(url_for('main'))


@app.route('/history/<int:patient_id>')
def history(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    falls = [{'timestamp': fall.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for fall in patient.falls]
    return jsonify({'falls': falls})


### Database End ###

@socketio.on('get_measurements')
def get_measurements():
    global connected
    while True: #need to change this for it to only work when connected
        data = get_data()
        prediction = get_predict()
        socketio.emit('measurements', {'data': data, 'classification': prediction,'prev':get_prev_classification(), 'status': connected})
        time.sleep(0.1)
        

if __name__ == '__main__':
    app.run()
