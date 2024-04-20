from time import sleep
from threading import Thread, Event

import requests


class Timelapse:
    def __init__(self, gopro):
        self.gopro = gopro
        self.interval = 10
        self.photos_taken = 0
        self.url = self.gopro.base_url + "/gopro/camera/presets/load?id=65536"
        self.timelapse_signal = Event()
        self._timelapse = Thread(
            target=self.timelapse_task, args=())

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
        assert (requests.get(self.url, timeout=2)).ok
        while not self.timelapse_signal.is_set():
            assert (requests.get(self.gopro.base_url +
                    "/gopro/camera/shutter/start", timeout=2)).ok
            self.photos_taken += 1
            sleep(self.interval)
        pass

    def is_running(self) -> bool:
        return self._timelapse.is_alive()