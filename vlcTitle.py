import os
import shutil
import sys
import time
import urllib.parse
import logging
import requests
from requests.auth import HTTPBasicAuth

from myFuncLib import ffmpegSimple

server = "http://127.0.0.1:8085/requests/status.json"
username = ""
password = "bruh"

filename = "currentVLCTitle.txt"
destination = "D:\\doku\\Python\\output\\"

selected = ["title", "artist"]
divider = " - "
prefix = "♫ "
postfix = " "

delay = 1
downtimeDelay = 3
defaultTimeout = 31
timeout=defaultTimeout

previousCover = ""
previousOutput = ""

# check args
def getArgs():
    try:
        if sys.argv[1] == "log":
            logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
        
        elif sys.argv[1] == "hide":   
            import win32gui, win32con
            window = win32gui.GetForegroundWindow()
            if win32gui.GetWindowText(window).endswith("python.exe") or win32gui.GetWindowText(window).endswith("py.exe"):
                win32gui.ShowWindow(window , win32con.SW_HIDE)
    
    except IndexError:
        pass

def getJSON(): # die dicke .json holen von dem vlc http server
    
    global timeout
    
    if timeout < defaultTimeout:
        time.sleep(delay + downtimeDelay - 2)
    
    timeout -= 1
    
    if timeout <= 0:
        logging.warning("Connection timed out after " + str(defaultTimeout - 1) + " attempts. Stopping program.")
        raise KeyboardInterrupt
    
    logging.info("connecting to " + server + "... ")
    r = requests.get(server, auth=HTTPBasicAuth(username, password)) # request schicken und einloggen
    while True:
        if r.status_code == 200:
            logging.info(r)
            r.encoding = 'utf-8' # << das rauszufinden hat irgendwie 3 stunden gedauert, awhnUIBFifawbjuogbaluoijgbn
            data = r.json() #die daten auslesen und zu einem dict umwandeln
            timeout=defaultTimeout
            return data
        elif r.status_code == 404:
            logging.info("Error! " + server + " konnte nicht erreicht werden!")
            pass
        else:
            logging.critical("lol keine ahnung was passiert ist")
            logging.critical(r.status_code)
            sys.exit()

def setVars(dict): #packt alles in ein einleveliges dict

    logging.info("Setting up properties... ")

    state = dict["state"] #zuerst kucken was vlc macht

    while not state == "playing" and not state == "paused":
        logging.info("Status: \"" + state + "\"")
        
        cleanup()
        
        time.sleep(delay + downtimeDelay)
        
        dict = getJSON()
        state = dict["state"]

    #zeit all die infos zu snacken ;p
    properties={}
    properties['currentTime'] = convertSeconds(dict["time"])
    properties['TotalLenght'] = convertSeconds(dict["length"])   #/60)[:4].replace(".", ":")

    metaData = dict["information"]["category"]["meta"]
    
    properties['backupName'] = metaData["filename"]
    
    try:
        properties['coverFilePath'] = urllib.parse.unquote(metaData["artwork_url"])[8:]
        noCover = False
    except KeyError:
        noCover = True
        
    try:
        properties['artist'] = metaData["artist"]
    except KeyError:
        pass
    
    try: 
        properties['album'] = metaData["album"]
    except KeyError:
        pass
        
    try:
        properties['title'] = metaData["title"]
    except KeyError:
        pass

    logging.info("Status: \"" + state + "\"")
    
    return properties, noCover

def selector(selection, selected):
    filteredOutput = []
    for i in selected:
        if i in selection:
            filteredOutput.append(selection[i])
    if filteredOutput == []:
        filteredOutput.append("".join(selection["backupName"].split(".")[0:-1])) #dateinamen ohne dateiendung in filteredOutput stecken
    return filteredOutput

def convertSeconds(seconds): 
    min, sec = divmod(seconds, 60) 
    hour, min = divmod(min, 60)
    return "%02d:%02d" % (min, sec)

def getCover(cover):

        global previousCover

        if not cover == previousCover or not os.path.isfile(destination + "art.jpg"):
            if cover.startswith("F:/"):
                if cover.endswith(".jpg"):
                    logging.info("Image found, copying...")
                    shutil.copy(cover, destination + "art.jpg")
                    logging.info("Copied successfully!")
                elif cover.endswith(".png"):
                    logging.info("Image found, converting...")
                    ffmpegSimple(input=cover, output=destination + "art.jpg", overwrite=True, quiet=True)
                    logging.info("Converted successfully!")
                else:
                    logging.info("Image not found...")
                    pass
            else:
                if cover.endswith("art.jpg"):
                    logging.info("Image found, copying...")
                    shutil.copy(cover, destination + "art.jpg")
                    logging.info("Copied successfully!")
                elif cover.endswith("art.png") or cover.endswith("art"):
                    logging.info("Image found, converting...")
                    ffmpegSimple(input=cover, output=destination + "art.jpg", overwrite=True, quiet=True)
                    logging.info("Converted successfully!")
                else:
                    logging.info("Image not found...")
                    pass
        previousCover = cover

def writeIt(FinalOutput):

    with open(destination + filename, "r", encoding="utf-8") as file:
        previousOutput = file.read()
    
    if not FinalOutput == previousOutput:

        logging.info("Writing to text file... ")

        with open(destination + filename, "w", encoding="utf-8") as txtOutput:
            txtOutput.write(prefix + divider.join(FinalOutput) + postfix) # schreiben in txtOutput, mit prefix,postfix und divider

        logging.info("wrote successfully!")

def cleanup():
    logging.info("Cleaning up... ")
    try:
        with open(destination + filename, 'w') as filetowrite: # entfernt text datei wenn sie existiert
            filetowrite.write('')
    except FileNotFoundError:
        pass
    try:
        os.remove(destination + "art.jpg") # entfernt cover wenn es existiert
    except FileNotFoundError:
        pass

def main():

        dict = getJSON() # json besorgen und zu dict umwandeln
        properties, noCover = setVars(dict) # variablen vorbereiten und überprüfen was vlc macht
        filteredOutput = selector(properties, selected) # die ausgeählten eigenschaften besorgen und in eine liste packen
        
        if noCover == False:
            coverPath = properties["coverFilePath"]
            getCover(coverPath) # das album cover besorgen und nach destination kopieren

        writeIt(filteredOutput) # currentVLCTitle.txt schreiben

if __name__ == '__main__':
    
    getArgs()
    
    while True:
        try:
            main()
            logging.info("Full loop complete.")
            time.sleep(delay)
        except requests.exceptions.ConnectionError: # verbindungs error ignorieren
            cleanup()
        except KeyboardInterrupt: # clean exit veruchen
            cleanup()
            sys.exit()