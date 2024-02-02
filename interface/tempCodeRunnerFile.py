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