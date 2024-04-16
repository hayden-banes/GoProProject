import asyncio
from open_gopro import WiredGoPro
from time import sleep
import requests, json
import ble_wakeup.ble_connect

class Utils:
    def __init__(self, identifier):
        self.identifier = identifier
        self.base_url = f"http://172.2{self.identifier[-3]}.1{self.identifier[-2:]}.51:8080"
        

    async def connect(self):
        attempts = 0 #Attempts to connect
        while attempts < 5:
            try:
                assert (requests.get(self.base_url + "/gopro/camera/control/wired_usb?p=1")).ok
                print("Connected!")
                attempts = 5
                return 0
            except Exception as e:
                print("Attempting wake up via BLE")
                await ble_wakeup.ble_connect.main(self.identifier)

            attempts += 1

        return 1 #failure

    def keep_alive(self, quit_signal):
        url = self.base_url + "/gopro/camera/keep_alive"
        while not quit_signal.is_set():
            response = requests.get(url, timeout = 2)
            # print(f"Response: {json.dumps(response.json(), indent=4)}")
            sleep(3)

    def set_base_url(self, identifier: str):
        self.base_url = f"http://172.2{self.identifier[-3]}.1{self.identifier[:-2]}.51:8080"

    def get_status(self):
        return requests.get(self.base_url + "/gopro/camera/state", timeout = 2)
