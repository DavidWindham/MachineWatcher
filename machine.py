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
    

class CommandEntry:
    def __init__(self, command_type, timestamp=None):
        self.command_type = command_type  # "on" or "off"
        self.timestamp = timestamp if timestamp is not None else time.time()
    
    def __repr__(self) -> str:
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))
        return f"Command: {self.command_type} at {time_str}"

    def to_dict(self):
        """Convert the command entry to a serializable dictionary"""
        return {
            "command_type": self.command_type,
            "timestamp": self.timestamp,
            "formatted_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))
        }

class MachineStatus:
    def __init__(self, base_url):
        self.base_url = base_url

        self.machine_on = False
        self.manager = Manager()
        self.machine_readings = self.manager.list()
        self.command_history = self.manager.list()  # New: track command history
        self.max_readings = 3600
        self.machine_turned_on_at = None
        self.last_turned_on_at = None  # New: to keep track of last time machine was on

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

    def record_command(self, command_type):
        """Record a command in the history"""
        command = CommandEntry(command_type)
        if len(self.command_history) >= self.max_readings:
            self.command_history.pop(0)
        self.command_history.append(command)

    def turn_machine_on(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": True})
        if call.status_code != 200:
            return "Error turning machine on"
        
        # Record this command in history
        self.record_command("on")
        
        # Let the status check handle setting machine_on = True
        # and starting the appropriate monitoring
        self.check_machine_status()
        return "Machine turned on"

    def turn_machine_off(self):
        call = requests.post(f"{self.base_url}/rpc/Switch.Set", json={"id": 0, "on": False})
        if call.status_code != 200:
            return "Error turning machine off"
        
        # Record this command in history
        self.record_command("off")
        
        # Save last turned on time before clearing it
        if self.machine_turned_on_at is not None:
            self.last_turned_on_at = self.machine_turned_on_at
        
        # Update state but preserve historical data
        self.machine_on = False
        self.machine_turned_on_at = None  # We clear this but keep last_turned_on_at
        
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
                self.last_turned_on_at = self.machine_turned_on_at
            else:
                # When turning off, we keep last_turned_on_at but clear machine_turned_on_at
                if self.machine_turned_on_at is not None:
                    self.last_turned_on_at = self.machine_turned_on_at
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
    
    def get_command_history(self):
        """Get the history of commands executed on the machine"""
        return [command.to_dict() for command in list(self.command_history)]
    
    def get_status(self):
        time_since_turned_on = None
        
        # Calculate time since machine was turned on if it's currently on
        if self.machine_on and self.machine_turned_on_at is not None:
            time_since_turned_on = time.time() - self.machine_turned_on_at
        
        return {
            "machine_on": self.machine_on,
            "machine_turned_on_at": self.machine_turned_on_at,
            "last_turned_on_at": self.last_turned_on_at,
            "time_since_turned_on": time_since_turned_on
        }
    
    def start_monitoring(self):
        """Initial start of the monitoring process"""
        self.check_machine_status()  # This will set the initial state and start appropriate monitoring