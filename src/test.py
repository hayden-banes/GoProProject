import requests
import json
from utils import GOPRO_BASE_URL

print("Starting...")

url = GOPRO_BASE_URL + "/gopro/camera/state"
response = requests.get(url, timeout=10)
print(f"Response: {json.dumps(response.json(), indent=4)}")