import requests

identifier = "4933"
base_url = f"http://172.2{identifier[-3]}.1{identifier[-2:]}.51:8080"


try:
    response = requests.get(base_url + "/gopro/camera/control/wired_usb?p=1", timeout=2)
except requests.Timeout as e:
    print("Timeout")

