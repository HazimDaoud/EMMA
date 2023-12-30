from flask import Flask, render_template, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random
import numpy as np
import time
from datetime import datetime
from flask_socketio import SocketIO

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
    return jsonify({'percentage': random.randint(0, 100), 'loading': random.choice([True, False])})


@app.route('/update_led')
def get_connection_status():
    return jsonify({'connected': random.choice([True, False, None])})


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
    name = "Max Mustermann"  # request.form.get('name')
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
    falls = patient.falls
    return render_template('history.html', patient=patient, falls=falls)
### Database End ###


@socketio.on('get_measurements')
def get_measurements():
    while True:
        data = [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]
        socketio.emit('measurements', {'data': data, 'classification': random.choice([True, False])})
        time.sleep(0.1)


if __name__ == '__main__':
    app.run()
