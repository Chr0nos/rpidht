#!env python3
from flask import Flask, jsonify
try:
    import Adafruit_DHT
except ModuleNotFoundError:
    Adafruit_DHT = None


app = Flask(__name__)


@app.route('/dht/mesurement', methods=['GET'])
def mesurement():
    assert Adafruit_DHT is not None
    sensor = Adafruit_DHT.AM2302
    pin = 23
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        return jsonify({
            'humidity': humidity,
            'temperature': temperature
        })
