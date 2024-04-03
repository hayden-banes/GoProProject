from time import sleep
from utils import GOPRO_BASE_URL
import requests

def keep_alive():
    url = GOPRO_BASE_URL + "/gopro/camera/keep_alive"
    while True:
        response = requests.get(url, timeout = 2)
        sleep(3)

print("I'll stay on for ever :(")
keep_alive()