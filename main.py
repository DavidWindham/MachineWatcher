from flask import Flask, send_from_directory, request, redirect
from machine import MachineStatus
from dotenv import load_dotenv
import os


app = Flask(__name__, static_folder='./frontend/dist', static_url_path='')

load_dotenv()

@app.before_request
def rewrite_api_prefix():
    if request.path.startswith('/api/'):
        new_path = request.path.replace('/api', '', 1)
        # Manually dispatch the rewritten request
        try:
            # Important: use current_app.full_dispatch_request() on a new request context
            from flask import current_app
            with current_app.request_context({
                **request.environ,
                'PATH_INFO': new_path
            }):
                return current_app.full_dispatch_request()
        except HTTPException as e:
            return e
    
@app.route('/')
def index():
    # return {"machine_status": machine_status.get_status()}
    return send_from_directory(app.static_folder, 'index.html')

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