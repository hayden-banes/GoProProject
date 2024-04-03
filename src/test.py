import requests
import json
from utils import GOPRO_BASE_URL
from time import sleep

print("Starting...")

url = GOPRO_BASE_URL + "/gopro/media/list"
response = requests.get(url, timeout=10)
print(f"Response: {json.dumps(response.json(), indent=4)}")

url = GOPRO_BASE_URL + "/gopro/camera/control/wired_usb?p=1"
response = requests.get(url, timeout=10)
print(f"Response: {json.dumps(response.json(), indent=4)}")

url = GOPRO_BASE_URL + "/gopro/camera/presets/load?id=1001"
response = requests.get(url, timeout=10)
print(f"Response: {json.dumps(response.json(), indent=4)}")

# url = GOPRO_BASE_URL + "/gopro/camera/shutter/start"
# response = requests.get(url, timeout=10)
# print(f"Response: {json.dumps(response.json(), indent=4)}")
# sleep(10)

# url = GOPRO_BASE_URL + "/gopro/camera/presets/get?id=186"
# response = requests.get(url, timeout=10)
# print(f"Response: {json.dumps(response.json(), indent=4)}")

# url = GOPRO_BASE_URL + "/gopro/camera/shutter/start"
# response = requests.get(url, timeout=10)
# print(f"Response: {json.dumps(response.json(), indent=4)}")
# sleep(10)

# url = GOPRO_BASE_URL + "/gopro/camera/shutter/stop"
# response = requests.get(url, timeout=10)
# print(f"Response: {json.dumps(response.json(), indent=4)}")