import asyncio
from time import sleep
from threading import Thread, Event

import requests
import ble_connect


class GoPro:
    def __init__(self, identifier):
        self.identifier = identifier
        self.base_url = self.generate_base_url()
        self.keep_alive_signal = Event()
        self._keep_alive = Thread(
            target=asyncio.run, args=(self.keep_alive_task(),)
        )
        self.connected = False
        
    def start(self):
        if not self.is_alive():
            print(f"Starting keep alive signal for GoPro {self.identifier}")
            self.set_auto_powerdown_off()
            self.keep_alive_signal.clear()
            self._keep_alive.start()
        else:
            print("Keep alive signal is already active")

    def stop(self):
        # Set the signal to send keep alive loop and stop attempting reconnect
        self.keep_alive_signal.set()
        # if the thread is still running, then stop it
        if self.is_alive():
            self._keep_alive.join()
        # create a new thread, as threads can only be started once
        self._keep_alive = Thread(target=self.keep_alive_task, args=())
        self.connected = False
        print("Keep alive signal stopped")  

    async def keep_alive_task(self):
        url = self.base_url + "/gopro/camera/keep_alive"
        while not self.keep_alive_signal.is_set():
            try:
                if not self.connected: await self.connect()
                assert (requests.get(url, timeout=2)).ok
            except requests.exceptions.RequestException as e:
                print("Failed to communicate with GoPro, retrying")
                self.connected = False
            sleep(3)

    async def connect(self) -> None:
        while not self.connected and not self.keep_alive_signal.is_set():
            try:
                response = requests.get(
                    self.base_url + "/gopro/camera/control/wired_usb?p=1", timeout=2)
                if response.ok:
                    print("Connected via USB!")
                    self.connected = True
                    return
            except requests.Timeout as e:
                print("Failed to enable wired control. Retrying wakeup")

            try:
                print("Attempting wake up via BLE")
                await ble_connect.connect_ble(self.identifier)

            except RuntimeError as e:
                print(f"Error connecting via BLE")

            print("Waiting for camera")
            sleep(10)


    async def check_gopro(self):
        if await self.connect():
            raise Exception(f"Could not connect to GoPro {self.identifier}")

    def is_alive(self) -> bool:
        return self._keep_alive.is_alive()

    def set_base_url(self):
        self.base_url = f"http://172.2{self.identifier[-3]}.1{self.identifier[:-2]}.51:8080"

    def get_status(self):
        return requests.get(self.base_url + "/gopro/camera/state", timeout=2)
    
    def start_shutter(self):
        return requests.get(self.base_url + "/gopro/camera/shutter/start", timeout=2)
    
    def generate_base_url(self) -> str:
        return f"http://172.2{self.identifier[-3]}.1{self.identifier[-2:]}.51:8080"
    
    def set_auto_powerdown_off(self):
        url = self.base_url + "/gopro/camera/setting?setting=59&option=0"
        requests.get(url, timeout=2)

    def set_auto_powerdown_on(self):
        url = self.base_url + "/gopro/camera/setting?setting=59&option=4"
        requests.get(url, timeout=2)
