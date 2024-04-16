import argparse
from utils import Utils
from threading import Thread, Event
from time import sleep
import requests



class GoProController():
    def __init__(self, args) -> None:
        self.args = args
        self.gopro = Utils(args.identifier)
        self.interval = 10
        self.photos_taken = 0

    def run(self) -> None:
        print("type h for help")

        try:
            #Check gopro exists/is connected
            # self.gopro.check()

            timelapse_signal = Event()
            keep_alive_signal = Event()
            _keep_alive = Thread(target=self.gopro.keep_alive, args=(keep_alive_signal,))
            _keep_alive.start()
        
            running = True

            while running:
                cmd = input()
                if cmd == "start":
                    print(f"Starting timelapse for GoPro {args.identifier}")
                    timelapse_signal.clear()
                    # TODO This can create endless threads, consider moving outside the loop so only one thread per GP
                    _timelapse = Thread(target=self.timelapse, args=(self.interval,timelapse_signal))
                    _timelapse.start()
                
                if cmd == "stop": # TODO will throw an exception is the thread is not running
                    if _timelapse.is_alive():
                        timelapse_signal.set()
                        _timelapse.join()
                        print("timelapse stopped")
                    else:
                        print("no timelapse active")

                if cmd == "status":
                    status = self.gopro.get_status().json()
                    print(f"Photos taken: {self.photos_taken}")
                    print(f"Photos remaing: {status['status']['34']}")
                
                if cmd == "download":
                    #TODO Can only work if timelapse has been run in this session
                    if _timelapse.is_alive():
                        print("please stop the current timelapse before downloading")
                    else:
                        self.download()

                if cmd == "h":
                    print("start")
                    print("stop")
                    print("status")
                    print("download")
                    print("q")

                elif cmd == "q":
                    running = False
                    break;
        

        except Exception as e:
            print(e)
            print(e.__traceback__.tb_lineno)
        
        print("Stopping background tasks", end="\r")
        timelapse_signal.set()
        print("Stopping background tasks.",end="\r")
        keep_alive_signal.set()
        print("Stopping background tasks..",end="\r")
        if _keep_alive.is_alive(): _keep_alive.join()
        print("Stopping background tasks...")
        if _timelapse.is_alive(): _timelapse.join()
        print("Goodbye!")

    def download(self):
        delete = input("Delete pictures from camera too? (y/n): ") == 'y'
        url = self.gopro.base_url + "/gopro/media/list"
        response = requests.get(url, timeout=2).json()

        count = 0 #Total images counter
        img_no = 0 #Transfered images counter

        for media in response['media']:
            count += len(media['fs'])

        for media in response['media']:
            for image in media['fs']:
                self.download_media(dest='/Users/hayden/GitHub/GoProProject/gproimg/', srcfolder=media['d'], srcimage=image['n'])

                #If delete flag is enabled
                if delete: self.delete_img(srcfolder=media['d'], srcimage=image['n'])

                #Provide an update on file transfer
                img_no+=1 
                if img_no % 5 == 0 : print(f'{round((img_no/count)*100,ndigits=2)}%', end="\r")
        
        print('100% - Done!') #To give a clean ending

    def download_media(self, dest, srcfolder, srcimage):
        url = self.gopro.base_url + f"/videos/DCIM/{srcfolder}/{srcimage}"
        try:
            with requests.get(url, timeout=2,stream=True) as response:
                response.raise_for_status()
                with open(f'{dest}{srcimage}', 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            print("error")

    def timelapse(self,interval,quit_signal):
        url = self.gopro.base_url + "/gopro/camera/presets/load?id=65536"
        response = requests.get(url, timeout = 2)
        while not quit_signal.is_set():
            assert(requests.get(self.gopro.base_url + "/gopro/camera/shutter/start", timeout=2)).ok
            self.photos_taken += 1
            sleep(interval)

    def set_auto_powerdown_off(self):
        url = self.gopro.base_url + "/gopro/camera/setting?setting=59&option=0"
        response = requests.get(url, timeout = 2)

    def set_auto_powerdown_on(self):
        url = "/gopro/camera/setting?setting=59&option=4"
        response = requests.get(url, timeout = 2)

    def delete_img(self, srcfolder, srcimage):
        url = self.gopro.base_url + f"/gopro/media/delete/file?path={srcfolder}/{srcimage}"
        response = requests.get(url, timeout=2)

    def upload_to_gdrive():
        return 1


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
    return parser.parse_args()



if __name__ == "__main__":
    args = parse_arguments()
    controller = GoProController(args)
    controller.run()