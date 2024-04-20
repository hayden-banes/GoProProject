import argparse
import asyncio
from pathlib import Path
from gopro import GoPro
from timelapse import Timelapse
from threading import Thread, Event
from time import sleep
import requests


class GoProController():
    def __init__(self, args) -> None:
        self.args = args
        self.gopro = GoPro(self.args.identifier)
        self.timelapse = Timelapse(self.gopro)
        self.keep_alive_signal = Event()
        self._keep_alive = Thread(
            target=self.gopro.keep_alive, args=(self.keep_alive_signal,))

        self.commands = ["start", "stop", "status",
                         "download", "clearSD", "h or help", "q or quit"]

    async def run(self) -> None:
        print("type h for help")

        try:
            # Check gopro exists/is connected
            await self.gopro.check_gopro()

            self._keep_alive.start()
            running = True

            while running:
                cmd = input()
                if cmd == "start":
                    self.timelapse.start()

                if cmd == "stop":
                    self.timelapse.stop()

                if cmd == "status":
                    self.status()

                if cmd == "interval":
                    self.timelapse.change_interval()

                if cmd == "download":
                    self.download()

                if cmd == "clearSD":
                    self.clear_sd()

                if cmd == "h" or cmd == "help":
                    self.show_help()

                if cmd == "q" or cmd == "quit":
                    running = False

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)  # type: ignore

        self.stop_tasks()

    def status(self):
        status = self.gopro.get_status().json()
        print(f"Photos taken this session: {self.timelapse.photos_taken}")
        print(f"Photos on SD card: {status['status']['38']}")
        print(f"Photos remaing: {status['status']['34']}")
        print(f"Timelapse interval: {self.timelapse.interval}")

    def download(self):
        if self.timelapse.is_running():
            print("Please stop the current timelapse before downloading")
            return

        delete = input("Delete pictures from camera too? (y/n): ") == 'y'
        url = self.gopro.base_url + "/gopro/media/list"
        response = requests.get(url, timeout=2).json()

        path = (Path(__file__).parent / "../gproimg/").resolve()

        count = 0  # Total images counter
        img_no = 0  # Transfered images counter

        for media in response['media']:
            count += len(media['fs'])

        for media in response['media']:
            for image in media['fs']:
                self.download_media(
                    dest=path, srcfolder=media['d'], srcimage=image['n'])

                # If delete flag is enabled
                # TODO Verify image has been safely downloaded before deleting
                if delete:
                    self.delete_img(srcfolder=media['d'], srcimage=image['n'])

                # Provide an update on file transfer
                img_no += 1
                if img_no % 5 == 0:
                    print(f'{round((img_no/count)*100,ndigits=2)}%', end="\r")

        print('100% - Done!')  # To give a clean ending

    def download_media(self, dest, srcfolder, srcimage):
        url = self.gopro.base_url + f"/videos/DCIM/{srcfolder}/{srcimage}"
        try:
            with requests.get(url, timeout=2, stream=True) as response:
                response.raise_for_status()
                with open(f'{dest}/{srcimage}', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            print("error")

    def clear_sd(self):
        if input("Confirm clear SD card? (y/n): ") == 'y':
            self.delete_all()
            print("SD Card Cleared")
        else:
            print("SD Card not cleared")

    def show_help(self):
        for cmd in self.commands:
            print(cmd)

    def stop_tasks(self):
        print("Stopping background tasks", end="\r")
        self.timelapse.stop(quiet=True)
        print("Stopping background tasks.", end="\r")
        self.keep_alive_signal.set()
        print("Stopping background tasks..", end="\r")
        if self._keep_alive.is_alive():
            self._keep_alive.join()
        print("Stopping background tasks...")
        print("Goodbye!")

    def set_auto_powerdown_off(self):
        url = self.gopro.base_url + "/gopro/camera/setting?setting=59&option=0"
        response = requests.get(url, timeout=2)

    def set_auto_powerdown_on(self):
        url = "/gopro/camera/setting?setting=59&option=4"
        response = requests.get(url, timeout=2)

    def delete_img(self, srcfolder, srcimage):
        url = self.gopro.base_url + \
            f"/gopro/media/delete/file?path={srcfolder}/{srcimage}"
        requests.get(url, timeout=2)

    def delete_all(self):
        url = self.gopro.base_url + "/gp/gpControl/command/storage/delete/all"
        requests.get(url, timeout=2)

    def upload_to_gdrive(self):
        return 1


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-identifier",
        type=str,
        help="last 4 digits of the serial number",
        nargs='?',
        default="4933"
    )
    parser.add_argument(
        "-interval",
        # "--interval",
        type=int,
        help="interval between photos in timelapse (default: 10. Can be changed later)",
        nargs='?',
        default=10
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    controller = GoProController(args)
    asyncio.run(controller.run())
