import argparse
from utils import keep_alive
from typing import Optional
from open_gopro import Params, WiredGoPro, proto
from threading import Thread, Event
from time import sleep
import asyncio



class timelaspse:
    def __init__

photos_taken = 0
interval = 10

async def main(args: argparse.Namespace) -> None:
    print("Started")

    try:
        async with WiredGoPro(args.identifier) as gopro:
            quit_signal = Event()
            _keep_alive = asyncio.create_task(keep_alive(gopro, quit_signal))
            # _keep_alive = Thread(target=keep_alive, args=(gopro, quit_signal,))
            # await _keep_alive.start()
            _timelapse = Thread(target=timelapse, args=(interval,gopro,quit_signal,))
            running = True

            while running:
                cmd = input()
                if cmd == "start":
                    print("Starting timelapse for gopro {identifier}")
                    await _timelapse.start()

                if cmd == "status":
                    print(photos_taken)

                elif cmd == "q":
                    await quit_signal.set()
                    await _keep_alive
                    await _timelapse.join()
                    await gopro.close()
                    running = False
                    break;
    

    except Exception as e:
        print(e)
    if gopro:
        await gopro.close()
    
    print("Goodbye!")

async def timelapse(interval,gopro,quit_signal):
    assert(await gopro.http_command.load_preset_group(group=proto.EnumPresetGroup.PRESET_GROUP_ID_PHOTO)).ok
    
    while not quit_signal.is_set():
        assert (await gopro.http_command.set_shutter(shutter=Params.Toggle.ENABLE)).ok
        photos_taken += 1
        sleep(interval)


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
    print(args)
    asyncio.run(main(args))