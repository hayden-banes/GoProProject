import requests
from utils import GOPRO_BASE_URL

def download_media(dest, srcfolder, srcimage):
    url = GOPRO_BASE_URL + f"/videos/DCIM/{srcfolder}/{srcimage}"
    try:
        with requests.get(url, timeout=2,stream=True) as response:
            response.raise_for_status()
            with open(f'{dest}{srcimage}', 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
    except requests.exceptions.RequestException as e:
        print("error")


#Media discovery
url = GOPRO_BASE_URL + "/gopro/media/list"
response = requests.get(url, timeout=2).json()
count = 0
for media in response['media']:
    count += len(media['fs'])

img_no = 0

for media in response['media']:
    # print(media['d'])
    for image in media['fs']:
        download_media(dest='/Users/hayden/GitHub/GoProProject/gproimg/', srcfolder=media['d'], srcimage=image['n'])
        img_no+=1
        if img_no % 5 == 0 : print(f'{round((img_no/count)*100,ndigits=2)}%', end="\r")




