from flask import Flask
from machine import MachineStatus
from dotenv import load_dotenv
import os


app = Flask(__name__)

load_dotenv()

@app.route('/')
def index():
    return {"machine_status": machine_status.get_status()}

@app.route('/turn_machine_on', methods=['POST'])
def turn_machine_on():
    return machine_status.turn_machine_on()

@app.route('/turn_machine_off', methods=['POST'])
def turn_machine_off():
    return machine_status.turn_machine_off()

@app.route('/get_machine_status')
def get_machine_status():
    readings = machine_status.get_readings()
    readings_json = []
    for reading in readings:
        readings_json.append(reading.__dict__)

    return {
        "status": machine_status.get_status(),
        "readings": readings_json
    }

if __name__ == '__main__':
    switch_url = os.getenv("switch_url")
    if switch_url is None:
        raise Exception("switch_url environment variable not set")
    
    machine_status = MachineStatus(base_url=switch_url)
    machine_status.check_machine_status()
    app.run(debug=True, host="0.0.0.0", port=5000)