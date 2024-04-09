import argparse
from utils import keep_alive, GOPRO_BASE_URL
from typing import Optional
from open_gopro import Params, WiredGoPro, proto
from threading import Thread, Event
from time import sleep
import asyncio
import requests, json

interval = 10
photos_taken = 0

def main(args: argparse.Namespace) -> None:
    print("type h for help")

    try:
        timelapse_signal = Event()
        keep_alive_signal = Event()
        _keep_alive = Thread(target=keep_alive, args=(keep_alive_signal,))
        _keep_alive.start()
       
        running = True

        while running:
            cmd = input()
            if cmd == "start":
                print(f"Starting timelapse for GoPro {args.identifier}")
                timelapse_signal.clear()
                _timelapse = Thread(target=timelapse, args=(interval,timelapse_signal))
                _timelapse.start()
            
            if cmd == "stop":
                if _timelapse.is_alive:
                    timelapse_signal.set()
                    _timelapse.join()
                    print("timelapse stopped")
                else:
                    print("no timelapse active")

            if cmd == "status":
                status = requests.get(GOPRO_BASE_URL + "/gopro/camera/state", timeout = 2).json()
                print(f"Photos taken: {photos_taken}")
                print(f"Photos remaing: {status['status']['34']}")

            elif cmd == "q":
                running = False
                break;
    

    except Exception as e:
        print(e)
        print(e.__traceback__.tb_lineno)
    
    print("Stopping processes...")
    timelapse_signal.set()
    keep_alive_signal.set()
    _keep_alive.join()
    if _timelapse.is_alive: _timelapse.join()
    print("Goodbye!")

def timelapse(interval,quit_signal):
    url = GOPRO_BASE_URL + "/gopro/camera/presets/load?id=65536"
    response = requests.get(url, timeout = 2)
    global photos_taken
    while not quit_signal.is_set():
        requests.get(GOPRO_BASE_URL + "/gopro/camera/shutter/start", timeout=2)
        photos_taken += 1
        sleep(interval)

def set_auto_powerdown_off():
    url = GOPRO_BASE_URL + "/gopro/camera/setting?setting=59&option=0"
    response = requests.get(url, timeout = 2)

def set_auto_powerdown_on():
    url = "/gopro/camera/setting?setting=59&option=4"
    response = requests.get(url, timeout = 2)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "identifier",
        type=str,
        help="last 4 digits of the serial number",
        nargs='?',
        default="4933"
    )
    parser.add_argument(
        "-d",
        "--interval"
    )
    type(parser.parse_args())
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_arguments()
    main(args)