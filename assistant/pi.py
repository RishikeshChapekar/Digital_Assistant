import paho.mqtt.client as paho
import sys
import os 
import wikipedia
import smtplib
import time
import atexit
import json
import urllib.request
import datetime
import subprocess
import speech_recognition as sr
import pyaudio
import RPi.GPIO as GPIO
import sqlite3
import random

broker="test.mosquitto.org"
port=1883
client1= paho.Client("control1")                           
client1.connect(broker,port)                                
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(18,GPIO.OUT)
millis = 0
ptime = 0
active = []
songList = []
_file = open("sysLogs.txt","a")
_file.write("LOGIN "+time.asctime(time.localtime(time.time()))+"\n")
_file.close()
songs = os.listdir("/home/pi/Music") #change it to wherever you've stored the music
r=sr.Recognizer()
m=sr.Microphone(device_index=2)
def listSongs():
    for i in range(0,len(songs)):
        songList.append(songs[i].lower())    
def speak(txt):
    os.system("espeak \""+txt+"\" ")
def loop():
    cmd=""
    r=sr.Recognizer()
    GPIO.output(18,GPIO.HIGH)
    with m as source:
         
         audio = r.listen(source)
         print("ready")
         GPIO.output(18,GPIO.LOW)
    try:
        cmd = r.recognize_google(audio)
        print(cmd)
        task(cmd)
    except sr.UnknownValueError:
        cmd = "xXxXxXxXx!@#*&^%$#"
        print(cmd)
        GPIO.output(18,GPIO.HIGH)
        task(cmd)
    except sr.RequestError as e:
        cmd = "xXxXxXxXx!@#*&^%$#"
        print(cmd)
        GPIO.output(18,GPIO.HIGH)
        task(cmd)        
def task(tsk):         
    if tsk in ["hello there","hello","hi there","hi","sup"]:
        speak("hello sir")
        loop()      
    elif tsk in ["good morning","good evening","good afternoon"]:
        speak(tsk)  
    elif "switch on" in tsk or "switch off" in tsk :
        a=tsk.split()
        stat=a[a.index("switch")+1]
        msg=""
        led = a[a.index("light")-1]
        # if led=="red" and stat=="on":
        #     msg="1r"
        # elif led=="red" and stat=="off":
        #     msg="0r"
        
        # if led=="green" and stat=="on":
        #     msg="1w"
        # elif led=="green" and stat=="off":
        #     msg="0w"
        
        # if led=="yellow" and stat=="on":
        #     msg="1y"
        # elif led=="yellow" and stat=="off":
        #     msg="0y"
        # mqttStuff(msg,stat)   You need an arduino for this 
    elif "open" in tsk and "chrome" in tsk:
        chrome(tsk)
    elif "play" in tsk.lower() and "music" in tsk.lower():
        music() 
    elif "play" in tsk.lower() and "instrumental" in tsk.lower():
        instrumental()       
    elif "play" in tsk.lower() and "music" not in tsk.lower():
        print(tsk[5:])
        if tsk[5:]=="instrumental" or tsk[5:]=="instrumental":
            instrumental()
        else:    
            playSong(tsk[5:].lower())
    elif "change the song" in tsk or "change song" in tsk or "next song" in tsk or "next track" in tsk:
        if "vlc" in active:
            changeTrack()
        else:
            music()       
    elif "close" in tsk:
        a = tsk.split()
        b = a.index("close")+1
        if a[b] == "chrome" or (a[b]=="the" and a[b+1]=="browser") or (a[b]=="google" and a[b+1]=="chrome"):
            closeProcess("chrome")
        elif a[b]=="music" or (a[b]=="the" and a[b+1] == "music") or a[b].lower()=="vlc":
            closeProcess("vlc")
        elif a[b]=="sublime" and a[b+1]=="text":
            closeProcess("subl")
        elif a[b]=="gedit":
            closeProcess("gedit")
        elif a[b] in ["everything","all"]:
            closeAll()
        elif a[b] in ["notes","xpad"]:
             closeProcess("xpad")
        else:
            loop()                            
    elif tsk in ["show all running processes","show all active processes", "what processes are running right now? ", "what are the processes active", "what all things are running", "give me details on all active processes", "i need details on all active processes","give me details on all running processes", "i need details on all running processes"]:
        showProcesses()
    elif tsk in ["i want to do some programming","i wanna do coding","open sublime text","i am in the mood to write some codes","open programming tool","open programming"]:
        speak("ok sir")
        stext("sub")
    elif tsk in ["i need to write something", "open plain text editor", "open text editor","open editor", "editor","i want to write","open gedit"]:
        speak("ok sir")
        stext("gedit")
    elif tsk in ["make a note","make a new note","create a note","note","show me all notes","show notes"]:
        note()      
    elif "search"  in tsk:
        speak("searching for "+ tsk[7:]+" on the net sir")
        wikisearch(tsk[7:]) 
    elif "go offline" in tsk:
        speak("Going offline now.....bye")
        quit()
    elif tsk=="shutdown":
        speak("closing all running programs and shutting down the computer")
        closeAndShut()
    elif "send" in tsk and "mail" in tsk:
        mail()
    elif "add a name to my mail list" in tsk or ("update" in tsk and "mail list" in tsk):
        updateList()    
    elif "show" in tsk and "mail list" in tsk:
        showMailList()
    elif "weather report" in tsk:
        a=tsk.split()
        city=a[a.index("for")+1]
        forecast(city)
    elif "what is the weather" in tsk:
        a=tsk.split()
        city=a[a.index("in")+1]
        forecast(city)          
    elif "date" in tsk and "time" not in tsk:
        datenow()
        loop()
    elif "time" in tsk and "date" not in tsk:
        timenow()
        loop()  
    elif tsk=="clear":
        os.system("clear")
        loop()  
    elif "remember" in tsk and "what" not in tsk:
        remember(tsk.split("remember")[1])
    elif "what" in tsk and "remember" in tsk and "thing" not in tsk:
        showrem()
    elif "what" in tsk and "remember" in tsk and " last thing" in tsk:
        showindexrem()      
    elif "send" in tsk and "random" in tsk and "image" in tsk:
        n = str(random(1,10000))+".jpg" 
        o = tsk.split()
        name = o[o.index("to")+1]
        randomImage(n,name)
    else:
        loop()  
          
def changeTrack():
    speak("changing track")
    os.system("pkill vlc")
    subprocess.Popen("cvlc /home/pi/Music", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)
    loop()                
def music():
    speak("playing music now")
    os.system("pkill vlc")
    try:
        active.remove("vlc")
    except:
        print("  ") 
    subprocess.Popen("cvlc /home/pi/Music", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)
    active.append("vlc")
    loop()
def playSong(song):
    play = ""
    os.system("pkill vlc")
    try:
        active.remove("vlc")
    except:
        print("vlc already removed")
    for i in range(0,len(songList)):
        if song in songList[i]:
            play = songs[i]
            speak("playing "+song+" for you ")
            break
        if i==len(songList)-1 and song not in songList[i]:
            speak("couldn't find "+song+" in your system sir. Playing something else in its place")
            break
    print(play)
    subprocess.Popen("cvlc /home/pi/Music/\""+play+"\"", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,shell=True)       
    # os.system("gnome-terminal -x vlc /home/pi/Music/\""+play+"\"")
    active.append("vlc")        
    loop()
def instrumental():
    os.system("pkill vlc")
    speak("playing instrumental music for you")
    subprocess.Popen("cvlc /home/pi/inst-music",stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,shell=True)
    loop()                  
def wikisearch(text):
    try:
        print(wikipedia.summary(text, sentences=4)) 
        speak(wikipedia.summary(text, sentences=4).replace("\"",""))
    except:
        speak("Couldn't find anything on the net for "+ text+ "sir. Maybe you have a spelling mistake") 
    loop()
def closeAll():
    speak("shutting down all processes currently active")
    for x in active:
        os.system("pkill "+x)
        active.remove(x)    
    loop()      
def closeProcess(process):
    speak("shuttin down "+process)
    os.system("pkill "+process)
    print(process)
    active.remove(process)
    loop()
def closeAndShut():
    for x in active:
        active.remove(x);
        os.system("pkill "+x)
    speak("have a nice day")
    os.system("poweroff")           
def showProcesses():
    if len(active)==0:
        speak("there are no processes running currently sir")
        loop()
    else:   
        speak("these are the processes currently running on your system sir")
        for prc in active:
            if prc=="subl":
                print("sublime text")
            else:
                print(prc)
        loop()  
 
def exit():
    file = open("sysLogs.txt", "a")
    file.write(" LOGOUT "+ time.asctime(time.localtime(time.time()))+"\n")
    speak("going offline")
    GPIO.output(18,GPIO.LOW)
def forecast(city):
    file=open("cityList.txt","r")
    cont=file.read().split()
    ID = cont.index(city)-1
    show(cont[ID])
def show(a):
    millis = int(round(time.time()))
    if __name__ == '__main__':
            data_output(data_organizer(data_fetch(url_builder(a)))) 
               
    loop()        
def time_converter(time):
    converted_time = datetime.datetime.fromtimestamp(
        int(time)
    ).strftime('%I:%M %p')
    return converted_time


def url_builder(city_id):
    user_api = 'fb6b0f5fdb937afaeb73100f0613257a'  # Obtain yours form: http://openweathermap.org/
    unit = 'metric'  # For Fahrenheit use imperial, for Celsius use metric, and the default is Kelvin.
    api = 'http://api.openweathermap.org/data/2.5/weather?id='     # Search for your city ID here: http://bulk.openweathermap.org/sample/city.list.json.gz

    full_api_url = api + str(city_id) + '&mode=json&units=' + unit + '&APPID=' + user_api
    return full_api_url


def data_fetch(full_api_url):
    url = urllib.request.urlopen(full_api_url)
    output = url.read().decode('utf-8')
    raw_api_dict = json.loads(output)
    url.close()
    return raw_api_dict


def data_organizer(raw_api_dict):
    data = dict(
        city=raw_api_dict.get('name'),
        country=raw_api_dict.get('sys').get('country'),
        temp=raw_api_dict.get('main').get('temp'),
        temp_max=raw_api_dict.get('main').get('temp_max'),
        temp_min=raw_api_dict.get('main').get('temp_min'),
        humidity=raw_api_dict.get('main').get('humidity'),
        pressure=raw_api_dict.get('main').get('pressure'),
        sky=raw_api_dict['weather'][0]['main'],
        sunrise=time_converter(raw_api_dict.get('sys').get('sunrise')),
        sunset=time_converter(raw_api_dict.get('sys').get('sunset')),
        wind=raw_api_dict.get('wind').get('speed'),
        wind_deg=raw_api_dict.get('deg'),
        dt=time_converter(raw_api_dict.get('dt')),
        cloudiness=raw_api_dict.get('clouds').get('all')
    )
    return data


def data_output(data):
    m_symbol = '\xb0' + 'C'
    a = str(format(data['temp'])).split(".")
    b = str(format(data['temp_max'])).split(".")
    c = str(format(data['temp_min'])).split(".")
    speak('Current weather in: {}, {}:'.format(data['city'], data['country']))
    if len(a)>1:
        speak("Current temperature:  "+a[0]+"point"+a[1] + "degrees Celsius")
    else:
        speak("Current temperature:  "+format(data['temp'])+ "degrees Celsius") 
    speak("sky shows"+data['sky'])
    if len(b)>1:
        speak("Maximum temperature: "+b[0]+"point"+b[1]+ "degrees Celsius")
    else:
        speak("Maximum temperatrue: "+format(data['temp_max'])+ "degrees Celsius")
    if len(c)>1:        
        speak("Minimum temperature: "+c[0]+"point"+c[1]+ "degrees Celsius")
    else:
        speak("Minimum temperature:  "+format(data['temp_min'])+ "degrees Celsius") 
    speak('Humidity: {}'.format(data['humidity'])+"percent")
    speak('Last update from the server: {}'.format(data['dt']))    
    print('---------------------------------------')
    print('Current weather in: {}, {}:'.format(data['city'], data['country']))
    print(data['temp'], m_symbol, data['sky'])
    print('Max: {}, Min: {}'.format(data['temp_max'], data['temp_min']))
    print('')
    print('Wind Speed: {}, Degree: {}'.format(data['wind'], data['wind_deg']))
    print('Humidity: {}'.format(data['humidity']))
    print('Cloud: {}'.format(data['cloudiness']))
    print('Pressure: {}'.format(data['pressure']))
    print('Sunrise at: {}'.format(data['sunrise']))
    print('Sunset at: {}'.format(data['sunset']))
    print('')
    print('Last update from the server: {}'.format(data['dt']))
    print('---------------------------------------')   

def remember(rem):
    cursor.exeute('''INSERT INTO remember VALUES(?,?)''',("null",rem))
    db.commit();
    speak("ok I will remember it")
    loop()
def showrem():
    speak("these are the things you asked me to remember")
    cursor.execute('''SELECT * FROM remember''')
    rem = cursor.fetchall();
    for rows in rem:
        speak(rows[1]);
    loop()
def showindexrem():
    speak("this is what you asked me to remember")
    cursor.execute('''SELECT * FROM remember ORDER BY sr LIMIT 1''')
    row = cursor.fetchone()
    speak(row[1])
    loop() 
def mqttStuff(message,status):
    ret= client1.publish("pikachu",message)
    speak("Done") 
    loop() 
def strangerThingsWill(req):
    if req==1:
        ret = client1.publish("pikachu", "1r")
        time.sleep(2)
        ret = client1.publish("pikachu","0r")
    if req==2:
        ret = client1.publish("pikachu","1r")
        time.sleep(0.5)
        ret = client1.publish("pikachu","0r")
        time.sleep(0.5)
        ret = client1.publish("pikachu","1r")
        time.sleep(0.5)
        ret = client1.publish("pikachu","0r")
        time.sleep(0.5)
    loop()          
atexit.register(exit)       
listSongs() 
speak("system ready")          
loop()
