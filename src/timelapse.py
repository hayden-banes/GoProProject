from time import sleep
from threading import Thread, Event
from datetime import datetime

import requests


class Timelapse:
    def __init__(self, gopro):
        self.gopro = gopro
        self.interval = 10
        self.photos_taken = 0
        self.timelapse_preset_url = self.gopro.base_url + "/gopro/camera/presets/load?id=65536"
        self.timelapse_signal = Event()
        self._timelapse = Thread(
            target=self.timelapse_task, args=())
        self.start_time = datetime.strptime("0800", "%H%M").time()
        self.end_time = datetime.strptime("1800", "%H%M").time()
        self.scheduled = False

    def start(self):
        if not self.is_running():
            print(f"Starting timelapse for GoPro {self.gopro.identifier}")
            self.timelapse_signal.clear()
            self._timelapse.start()
        else:
            print("Timelapse already running")

    def stop(self, quiet=False):
        if self.is_running():
            self.timelapse_signal.set()
            self._timelapse.join()
            print("Timelapse stopped")

            self.timelapse_signal.clear()
            self._timelapse = Thread(
                target=self.timelapse_task, args=())
        else:
            if not quiet: print("No timelapse active")

    def change_interval(self):
        cmd = input("Enter interval (seconds): ")
        if cmd.isnumeric() and (new_interval := int(cmd)) >= 3:
            self.interval = new_interval
            print(f"Interval changed to {self.interval}")
        else:
            print("Error: please enter a positive integer larger than 3")

    def timelapse_task(self):
        assert (requests.get(self.timelapse_preset_url, timeout=2)).ok
        while not self.timelapse_signal.is_set():
            if self.check_schedule():
                assert (self.gopro.start_shutter()).ok
                self.photos_taken += 1
            sleep(self.interval)

    def is_running(self) -> bool:
        return self._timelapse.is_alive()
    
    def check_schedule(self) -> bool:
        if self.scheduled:
            return (self.start_time <= datetime.now().time() <= self.end_time)
        
        return True
    
    def toggle_schedule(self):
        self.scheduled = not self.scheduled

    def set_schedule(self):
        print("use time format hhmm (e.g. 0800 or 1730)")
        start_time = input("Enter start time: ")
        end_time = input("Enter end time: ")
        if start_time.isnumeric() and end_time.isnumeric():
            try:
                self.set_start_time(start_time)
                self.set_end_time(end_time)
            except ValueError as e:
                print(e)
                
    def get_start_time(self) -> str:
        return self.start_time.strftime("%H%M")

    def get_end_time(self) -> str:
        return self.end_time.strftime("%H%M")
    
    def get_schedule(self) -> str:
        return f"{self.get_start_time()} - {self.get_end_time()}"

    def set_start_time(self, start_time:str):
        self.start_time = datetime.strptime(start_time, "%H%M").time()

    def set_end_time(self, end_time:str):
        self.end_time = datetime.strptime(end_time, "%H%M").time()

