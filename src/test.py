import argparse
from typing import Optional
from open_gopro import Params, WiredGoPro, proto
from threading import Thread, Event
from time import sleep
import asyncio

photos_taken = 0
interval = 10

async def main(identifier: Optional[str]) -> None:
    print("Started")

    try:
        quit_signal = Event()
        _keep_alive = Thread(target=keep_alive, args=(quit_signal,))
        _keep_alive.start()
        _timelapse = Thread(target=timelapse, args=(interval,quit_signal,))

        running = True
        while running:
            cmd = input()
            if cmd == "start":
                print("Starting timelapse for gopro {identifier}")
                _timelapse.start()

            if cmd == "status":
                print(photos_taken)

            elif cmd == "q":
                quit_signal.set()
                _keep_alive.join()
                if _timelapse.is_alive() : _timelapse.join()
                # await gopro.close()
                running = False
                break;
    

    except Exception as e:
        print(e)
    
    print("Goodbye!")

async def timelapse(interval,quit_signal):
    # set to photomode
    # set resolution and other photo settings
    
    while not quit_signal.is_set():
        #take picture
        photos_taken += 1
        sleep(interval)




def keep_alive(signal):
    while not signal.is_set():
        print("staying awake\r")
        sleep(3)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--identifier",
        type=str,
        help="last 4 digits of the serial number",
        default=None,
    )
    parser.add_argument(
        "-d",
        "--interval"
    )

    args = parser.parse_args()
    asyncio.run(main(args.identifier))