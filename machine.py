from multiprocessing import Process, Manager
import time
import json
import requests


class MachineDataPoint:
    def __init__(self, json):
        # auto json unpacking into object
        self.__dict__.update(json)
        self.timestamp = time.time()
    def __repr__(self) -> str:
        return f"Machine Status: {self.id}, {self.source}, {self.output}, {self.apower}, {self.voltage}, {self.current}, {self.aenergy}, {self.temperature}"
    

class MachineStatus:
    def __init__(self, base_url):
        self.base_url = base_url

        self.machine_on = False
        self.manager = Manager()
        self.machine_readings = self.manager.list()
        self.max_readings = 3600
        self.machine_turned_on_at = time.time()

        self.async_machine_caller_thread = None

    def is_async_thread_alive(self) -> bool:
        if hasattr(self, 'async_machine_caller_thread') is False:
            return False
        
        if self.async_machine_caller_thread is None:
            return False
        
        return self.async_machine_caller_thread.is_alive()
        
    
    def start_async_machine_caller_thread(self):
        if self.is_async_thread_alive():
            return
        
        self.async_machine_caller_thread = Process(target=self.check_machine_loop)
        self.async_machine_caller_thread.daemon = True
        self.async_machine_caller_thread.start()

    def stop_async_machine_caller_thread(self):
        if not self.is_async_thread_alive():
            return
        
        self.async_machine_caller_thread.terminate()

    def turn_machine_on(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": True})
        if call.status_code != 200:
            return "Error turning machine on"
        
        self.machine_on = True
        self.machine_turned_on_at = time.time()
        self.start_async_machine_caller_thread()

        return "Machine turned on"

    def turn_machine_off(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": False})
        if call.status_code != 200:
            return "Error turning machine off"
        
        self.machine_on = False
        self.machine_turned_on_at = None
        if self.is_async_thread_alive():
            self.async_machine_caller_thread.terminate()
        self.machine_readings = self.manager.list()
        self.check_machine_status()
        
        return "Machine turned off"

    def check_machine_loop(self):
        while True:
            self.check_machine_status()

    def check_machine_status(self):
        time_start = time.time()
        call = requests.post(f"{self.base_url}/rpc/Switch.GetStatus", json={"id": 0})
        data = call.json()
        data['timestamp'] = time.time()
        new_reading = MachineDataPoint(data)


        if new_reading.output == False:
            self.machine_on = False
            self.stop_async_machine_caller_thread()
        if new_reading.output == True:
            self.machine_on = True
            self.start_async_machine_caller_thread()
            
        self.record_reading(new_reading)

        time_end = time.time()
        time_delta = time_end - time_start
        if 1 - time_delta > 0:
            time.sleep(1 - (time_end - time_start))
        time_start = time.time()


    def record_reading(self, reading):
        if len(self.machine_readings) > self.max_readings:
            self.machine_readings.pop(0)
        self.machine_readings.append(reading)

    def get_readings(self):
        return self.machine_readings
    
    def get_status(self):
        time_since_turned_on = None
        if self.machine_turned_on_at is None:
            self.machine_turned_on_at = time.time() - time.time()
        else:
            time_since_turned_on = time.time() - self.machine_turned_on_at
        return {
            "machine_on": self.machine_on,
            "machine_turned_on_at": self.machine_turned_on_at,
            "time_since_turned_on": time.time() - self.machine_turned_on_at
        }