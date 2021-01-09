#!env python3
from flask import Flask, jsonify
import smbus2
import bme280


app = Flask(__name__)
port = 1
address = 0x76
bus = smbus2.SMBus(port)

calibration_params = bme280.load_calibration_params(bus, address)


@app.route('/dht/mesurement', methods=['GET'])
def mesurement():
    data = bme280.sample(bus, address, calibration_params)
    fields = ('id', 'timestamp', 'temperature', 'humidity', 'pressure')
    return jsonify({k: getattr(data, k) for k in fields})

