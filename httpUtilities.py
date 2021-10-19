
# public variable for http request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Connection': 'keep-alive',
    'Refer': 'https://www.google.com'
}

import os
import time
import random
import requests
import urllib.parse
import ntpath


def randDelay(min:float, max:float) -> None:
    n = random.uniform(min, max)
    time.sleep(round(n, 2))

def downloadFile(url:str, filepath:str) -> None:
    filepath = os.path.abspath(filepath)
    loc_filepath = ""
    # handle unspecified filename
    if os.path.isdir(filepath) or not os.path.isfile(filepath):
        parse1 = urllib.parse.urlparse(url)
        loc_filepath = os.path.join(filepath, ntpath.basename(parse1.path))
    else: loc_filepath = filepath
    # get file
    resp = requests.get(url=url, headers=HEADERS)
    # write file
    with open(loc_filepath, 'wb') as file:
        file.write(resp.content)

def getSrc(url:str) -> str:
    resp = requests.get(url=url, headers=HEADERS)
    return resp.text

def getSrcJson(url:str) -> dict:
    resp = requests.get(url=url, headers=HEADERS)
    return resp.json()


def writeStr2File(data:str, filepath:str, encoding="ascii") -> None:
    with open(filepath, 'w', encoding=encoding) as file:
        file.write(data)

def writeBytes2File(data:bytes, filepath:str) -> None:
    with open(filepath, 'wb') as file:
        file.write(data)
