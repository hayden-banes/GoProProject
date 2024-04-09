from open_gopro import WiredGoPro
from time import sleep
import requests, json

GOPRO_BASE_URL = "http://172.29.133.51:8080"

def keep_alive(quit_signal):
    url = GOPRO_BASE_URL + "/gopro/camera/keep_alive"
    while not quit_signal.is_set():
        response = requests.get(url, timeout = 2)
        # print(f"Response: {json.dumps(response.json(), indent=4)}")
        sleep(3)
