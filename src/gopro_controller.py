import datetime
from pathlib import Path
from gopro import GoPro
from timelapse import Timelapse
from PIL import Image

import os
import argparse
import asyncio
import requests


class GoProController():
    def __init__(self, args):
        self.args = args
        self.gopro = GoPro(self.args.identifier)
        self.timelapse = Timelapse(self.gopro)

    async def run(self):
        print("type h for help")

        try:
          
            running = True

            while running:
                # Check gopro exists/is connected
                if not self.gopro.is_alive():
                    self.timelapse.stop()
                    self.gopro.stop()
                    await self.gopro.check_gopro()
                    self.gopro.start()

                cmd = input()
                if cmd == "start":
                    self.timelapse.start()

                if cmd == "stop":
                    self.timelapse.stop()

                if cmd == "status":
                    self.status()

                if cmd == "interval":
                    self.timelapse.change_interval()
                
                if cmd == "tschedule":
                    self.timelapse.toggle_schedule()
                
                if cmd == "sschedule":
                    self.timelapse.set_schedule()

                if cmd == "download":
                    self.download()

                if cmd == "clearSD":
                    self.clear_sd()
                
                if cmd == "retry":
                    print("Retrying connections")

                if cmd == "h" or cmd == "help":
                    self.show_help()

                if cmd == "q" or cmd == "quit":
                    running = False

        except Exception as e:
            print(e)
            print(f"Error occured on line: {e.__traceback__.tb_lineno}")  # type: ignore

        self.stop_tasks()

    def status(self):
        status = self.gopro.get_status().json()
        print(f"Photos taken this session: {self.timelapse.photos_taken}")
        print(f"Photos on SD card: {status['status']['38']}")
        print(f"Photos remaing: {status['status']['34']}")
        print(f"Timelapse interval: {self.timelapse.interval}")
        print(f"Timelapse schedued? {self.timelapse.scheduled}")
        if self.timelapse.scheduled: print(f"Timelapse schedule {self.timelapse.get_schedule()}")

    def download(self):
        try:
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
            
            print(f"{count} files found")

            for media in response['media']:
                folder = media['d']
                if not os.path.exists(f"{path}/{folder}"):
                    os.makedirs(f"{path}/{folder}")

                for image in media['fs']:
                    image = image['n']
                    self.download_media(
                        dest=path, srcfolder=folder, srcimage=image
                        )
                    
                    if self.fix_metadata(f"{path}/{folder}/{image}"):
                        
                        # If delete flag is enabled
                        # The image can only be downloaded from the camera if it can be found locally
                        if delete:
                            self.delete_img(srcfolder=folder, srcimage=image)

                    # Provide an update on file transfer
                    img_no += 1
                    if img_no % 5 == 0:
                        print(f'{round((img_no/count)*100,ndigits=2)}%', end="\r")

            print('100% - Done!')  # To give a clean ending

        except FileNotFoundError as e:
            print("Error operating on files")
            print(e)
            print(e.__traceback__.tb_lineno) # type: ignore

    def fix_metadata(self, path) -> bool:
        '''
        Returns true if the file can be found
        '''
        img = Image.open(path)
        if not img: return False
        exif_data = img.getexif()
        if exif_data:
            timestamp = exif_data.get(306) or exif_data.get(36867)
            if timestamp:
                cre = datetime.datetime.strptime(
                timestamp, "%Y:%m:%d %H:%M:%S").timestamp()
                os.utime(path, times=(cre, cre))
        else:
            print("Warning: Timestamp may be incorrect on file")
        return True

    def download_media(self, dest, srcfolder, srcimage):
        url = self.gopro.base_url + f"/videos/DCIM/{srcfolder}/{srcimage}"
        path = f"{dest}/{srcfolder}/{srcimage}"

        try:
            #Download Image
            with requests.get(url, timeout=2, stream=True) as response:
                response.raise_for_status()
                with open(path, 'wb') as f:
                    f.write(response.content)
            
        except requests.exceptions.RequestException as e:
            print("error")

    def clear_sd(self):
        if input("Confirm clear SD card? (y/n): ") == 'y':
            self.delete_all()
            print("SD Card Cleared")
        else:
            print("SD Card not cleared")

    def show_help(self):
        commands = ["start", "stop", "status",
                    "download", "clearSD", "h or help", "q or quit"]
        for cmd in commands:
            print(cmd)

    def stop_tasks(self):
        print("Stopping background tasks", end="\r")
        self.timelapse.stop()
        print("Stopping background tasks.", end="\r")
        self.gopro.stop()
        print("Stopping background tasks..", end="\r")
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
