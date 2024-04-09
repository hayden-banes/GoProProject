from open_gopro import WiredGoPro, proto, Params
from time import sleep
import requests, json
import asyncio

async def keep_alive(gopro: WiredGoPro, signal):
    print("here")
    while not signal.is_set():
        # response = requests.get(url, timeout = 2)
        try:
            print("keeping alive")
            assert(await gopro.http_command.set_keep_alive()).ok
        except Exception as e:
            print(e)
            return;
        # print(f"Response: {json.dumps(response.json(), indent=4)}")
        sleep(3)