import os
import math
import time
import zipfile
import requests
import argparse
from datetime import timedelta
from requests.adapters import HTTPAdapter
from urllib.parse import urlparse, urlunparse
from requests.packages.urllib3.util.retry import Retry

#function returns ETA
def calcETA(startTime, currentTime,  zipFileSize, currentSize):

    if currentSize == 0:
        return None
    diff = currentTime - startTime
    rate = currentSize/diff
    eta = int(float((zipFileSize) - float(currentSize)) / rate)
    return timedelta(seconds=eta)

#function returns progress percentage
def calcPercent(zipFileSize, currentSize):

    if currentSize == 0:
        return None
    return round((currentSize/zipFileSize) * 100.0, 2)

#function returns taken time
def calcElaspedTime(startTime, currentTime):

    return timedelta(seconds=currentTime - startTime)

#function returns download speed
def calcSpeed(startTime, currentTime, currentSize):

    if currentSize == 0:
        return None
    diff = currentTime - startTime
    rate = currentSize/diff
    return formatBytes(rate)

#function takes bytes and returns formatted string
def formatBytes(bytes):

    if bytes == 0:
        return "0B"
    suffixes = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']
    index = int(math.floor(math.log(bytes, 1024)))
    formatted = round(float(bytes)/(1024**index), 2)
    return f"{formatted} {suffixes[index]}"

#variable declarations
DOMAIN = "www.dropbox.com"
WGET_AGENT = "Wget/1.19.4 (linux-gnu)"
RETRIES = Retry(total=10, backoff_factor=2)
ERASE = "\033[2K"

#argument parser
argsParser = argparse.ArgumentParser(description="python script to download dropbox public folders as zip files")
groupArgsParser = argsParser.add_mutually_exclusive_group()
groupArgsParser.add_argument("--links" ,type=str, nargs="+", const=None, help="read links from STDI")
groupArgsParser.add_argument("--read" ,metavar="file.txt", type=argparse.FileType("r", encoding="UTF-8"), const=None, help="read links from file")
argsParser.add_argument("--dest" ,type=str, default=os.getcwd(), help="specify download directory") 
argsParser.add_argument("--unzip", action="store_true", help="unzip downloaded zipfiles into folders and delete zipfiles")
argsParser.add_argument("--retain_zip", action="store_true", help="don't delete zipfiles after unzipping when --unzip is used")
arguments = argsParser.parse_args() #use this to access supplied arguments

#check if argument is supplied, if not, exit
if not (arguments.read or arguments.links):

    print("[-] No options specified, use --help for available options")
    exit()

else:

    # convert the supplied links into list
    if arguments.links:
        suppliedLinks = list(dict.fromkeys(arguments.links)) 

    # read given file and add each line to list
    else:
        suppliedLinks = list(dict.fromkeys(list(arguments.read.read().splitlines())))
        arguments.read.close()

# destination folder supplied by the user
destination = arguments.dest
print(f"\n[location] Specified download location: {destination}")

#check if unzip argument is supplied
if arguments.unzip:
    if arguments.retain_zip:
        print(f"\n[info] zipfiles will not be deleted after unzipping")
    elif not arguments.retain_zip:
        print(f"\n[info] --unzip was used without --retain_zip, zipfiles will be deleted after unzipping")

#iterate thru' links in the list
for suppliedLink in suppliedLinks:
    
    parsedURL = urlparse(suppliedLink)

    #check if link belongs to www.dropbox.com
    if not parsedURL.netloc ==  DOMAIN:
        print(f"\n[ERROR] {suppliedLink} does not belong to {DOMAIN}, skipping it ")
        continue

    #add query to make link downloadable as zip
    zippedDownloadURL = urlunparse(parsedURL._replace(query="dl=1"))
    print(f"\n[url] Downloading from URL : {suppliedLink}")

    with requests.Session() as session:
        session.mount("https://", HTTPAdapter(max_retries=RETRIES)) 

        try:
            zipFileResp = session.get(zippedDownloadURL, headers={"User-Agent" : WGET_AGENT}, timeout=60, stream=True)
            startTime = time.time()
            zipFileResp.raise_for_status()

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] Unable to retrieve {suppliedLink}, due to network error")
            continue

        except requests.exceptions.Timeout:
            print(f"[ERROR] Unable to retrieve {suppliedLink}, connection timed out")
            continue

        except requests.exceptions.HTTPError as err:
            print(f"[ERROR] {err}")
            continue

        zipFilename = zipFileResp.headers["content-disposition"].split(";")[1].split('"')[1] #get filename from response headers
        zipFileSize = float(zipFileResp.headers['Content-Length']) #get file size from response headers
        formattedZipFileSize = formatBytes(zipFileSize)
        filePath = os.path.join(destination, zipFilename) #path to store the file
        tempFilePath = os.path.join(destination, f"{zipFilename}.part") #path to store file with temporary filename
        
        print(f"[file] Downloading file : {zipFilename}")

        currentSize = 0
        try:
            with open(tempFilePath, "wb") as zipFile: #write file to disk

                for chunk in zipFileResp.iter_content(chunk_size=2**20):

                    if chunk:
                        
                            currentSize += len(chunk)
                            zipFile.write(chunk)
                            zipFile.flush()
                            os.fsync(zipFile.fileno())
                            progress = calcPercent(zipFileSize, currentSize)
                            eta = calcETA(startTime, time.time(),  zipFileSize, currentSize)
                            speed = calcSpeed(startTime, time.time(), currentSize)
                            print(f"[downloading] {progress}% of {formattedZipFileSize} at {speed}ps ETA {eta}", end="\r", flush=True)

        except KeyboardInterrupt:
            print(f"[downloaded] {progress}% of {formattedZipFileSize} at {speed} ps ETA {eta}")
            print("[ERROR]: Interrupted by user")
            exit()

        #print messaage when download is over
        if os.stat(tempFilePath).st_size == zipFileSize:
            os.rename(tempFilePath, filePath)
            print(ERASE, end="\r", flush=True)
            print(f"[downloaded] 100% of {formattedZipFileSize} in {calcElaspedTime(startTime, time.time())}")
    
    #if unzip argument is used unzip files
    if arguments.unzip:

        with zipfile.ZipFile(filePath, "r") as zipFile:

            directoryName = zipFilename.replace(".zip", "")
            directoryPath = os.path.join(destination, directoryName)
            os.makedirs(directoryPath, exist_ok=True)
            zipFile.extractall(directoryPath)
        
        #check if zip files should be deleted
        if not arguments.retain_zip:
            os.remove(filePath)
            
