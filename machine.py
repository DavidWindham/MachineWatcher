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
        self.machine_turned_on_at = None

        # Ping intervals in seconds
        self.ON_PING_INTERVAL = 1
        self.OFF_PING_INTERVAL = 20
        
        self.async_machine_caller_thread = None

    def is_async_thread_alive(self) -> bool:
        if hasattr(self, 'async_machine_caller_thread') is False:
            return False
        
        if self.async_machine_caller_thread is None:
            return False
        
        return self.async_machine_caller_thread.is_alive()
    
    def start_async_machine_caller_thread(self):
        if self.is_async_thread_alive():
            self.stop_async_machine_caller_thread()
        
        self.async_machine_caller_thread = Process(target=self.check_machine_loop)
        self.async_machine_caller_thread.daemon = True
        self.async_machine_caller_thread.start()

    def stop_async_machine_caller_thread(self):
        if not self.is_async_thread_alive():
            return
        
        self.async_machine_caller_thread.terminate()
        self.async_machine_caller_thread = None

    def turn_machine_on(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": True})
        if call.status_code != 200:
            return "Error turning machine on"
        
        # Let the status check handle setting machine_on = True
        # and starting the appropriate monitoring
        self.check_machine_status()
        return "Machine turned on"

    def turn_machine_off(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": False})
        if call.status_code != 200:
            return "Error turning machine off"
        
        # Let the status check handle setting machine_on = False
        # and adjusting the monitoring
        self.machine_on = False
        self.machine_turned_on_at = None
        if self.is_async_thread_alive():
            self.async_machine_caller_thread.terminate()
        self.machine_readings = self.manager.list()
        self.check_machine_status()
        return "Machine turned off"

    def check_machine_loop(self):
        while True:
            time_start = time.time()
            self.check_machine_status()
            time_end = time.time()
            
            # Determine sleep time based on machine status
            sleep_interval = self.ON_PING_INTERVAL if self.machine_on else self.OFF_PING_INTERVAL
            time_delta = time_end - time_start
            
            if sleep_interval - time_delta > 0:
                time.sleep(sleep_interval - time_delta)

    def check_machine_status(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.GetStatus", json={"id": 0})
        data = call.json()
        data['timestamp'] = time.time()
        new_reading = MachineDataPoint(data)

        # Store the reading
        self.record_reading(new_reading)
        
        # Detect state changes
        previous_state = self.machine_on
        current_state = new_reading.output
        
        # Update state if it changed
        if previous_state != current_state:
            self.machine_on = current_state
            
            # Record when machine was turned on
            if current_state:
                self.machine_turned_on_at = time.time()
            else:
                self.machine_turned_on_at = None
            
            # Restart the monitoring thread with appropriate interval
            self.restart_monitoring()

    def restart_monitoring(self):
        """Restart monitoring with the appropriate interval based on machine state"""
        if self.is_async_thread_alive():
            self.stop_async_machine_caller_thread()
        self.start_async_machine_caller_thread()

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
            "time_since_turned_on": time_since_turned_on
        }
    
    def start_monitoring(self):
        """Initial start of the monitoring process"""
        self.check_machine_status()  # This will set the initial state and start appropriate monitoring
