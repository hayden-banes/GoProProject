from time import sleep
import requests
import ble_wakeup.ble_connect

class GoPro:
    def __init__(self, identifier):
        self.identifier = identifier
        self.base_url = f"http://172.2{self.identifier[-3]}.1{self.identifier[-2:]}.51:8080"

    async def connect(self):
        attempts = 0  # Attempts to connect
        while attempts < 5:
            try:
                attempts += 1
                print("Attempting wake up via BLE")
                client = await ble_wakeup.ble_connect.connect_ble(self.identifier)
                await client.disconnect()

            except RuntimeError as e:
                print(e)
                print("No bluetooth devices were found, maybe its already on?")

            # Try HTTP request
            try:
                response = requests.get(
                    self.base_url + "/gopro/camera/control/wired_usb?p=1", timeout=10)
                if response.ok:
                    print("Connected!")
                    attempts = 5
                    return 0
            except Exception as e:
                print(e)

        return 1  # failure

    async def check_gopro(self):
        if await self.connect():
            raise Exception(f"Could not connect to GoPro {self.identifier}")

    def keep_alive(self, quit_signal):
        url = self.base_url + "/gopro/camera/keep_alive"
        while not quit_signal.is_set():
            response = requests.get(url, timeout=2)
            # print(f"Response: {json.dumps(response.json(), indent=4)}")
            sleep(3)

    def set_base_url(self, identifier: str):
        self.base_url = f"http://172.2{self.identifier[-3]}.1{self.identifier[:-2]}.51:8080"

    def get_status(self):
        return requests.get(self.base_url + "/gopro/camera/state", timeout=2)
