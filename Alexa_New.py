#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Libs
# cd F:\Program Files\Anaconda>python -m PyQt5.uic.pyuic -x RehoboamUI.ui -o RehoboamUI.py
import pyttsx3
import speech_recognition as sr
import datetime
import os
import cv2
import random
import wikipedia
import webbrowser
import pywikihow
import pywhatkit
import sys
import pyautogui
import requests, geocoder
import pytz
import time
import requests
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUiType
from RehoboamUI import Ui_Form
#from ipynb.fs.full.RehoboamUI import *


# In[3]:


def override_where():
    """ overrides certifi.core.where to return actual location of cacert.pem"""
    # change this to match the location of cacert.pem
    return os.path.abspath("cacert.pem")


# is the program compiled?
if hasattr(sys, "frozen"):
    import certifi.core

    os.environ["REQUESTS_CA_BUNDLE"] = override_where()
    certifi.core.where = override_where

    # delay importing until after where() has been replaced
    import requests.utils
    import requests.adapters
    # replace these variables in case these modules were
    # imported before we replaced certifi.core.where
    requests.utils.DEFAULT_CA_BUNDLE_PATH = override_where()
    requests.adapters.DEFAULT_CA_BUNDLE_PATH = override_where()


# In[2]:


listener = sr.Recognizer()
voice = pyttsx3.init()
voice.setProperty('rate', 125)

def speak(audio):
    voice.say(audio)
    voice.runAndWait()
    
def wish():
    hour = int(datetime.datetime.now().hour)
    speak('Hello!')
    if hour>=0 and hour<=12:
        speak('good morning sir')
    elif hour>12 and hour<18:
        speak('good afternoon sir')
    else:
        speak('good evening sir')


# In[3]:


def news():
    main_url='https://newsapi.org/v2/top-headlines?country=us&apiKey=e4f5414cddf2443b817cbfd1cf0b83be'
    
    main_page = requests.get(main_url).json()
    articles = main_page['articles']
    head = []
    day = ['first','second','third','fourth','fifth','sexth','seventh','eighth','neith','tenth']
    for ar in articles:
        head.append(ar['title'])
    for i in range(len(day)):
        speak(f"today's {day[i]} news is: {head[i]}")


# In[4]:


class WorkerSignals(QObject):
# 1
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


# In[ ]:


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        # 2
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress
    
    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print('listening..')
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=15, phrase_time_limit=5)

            try:
                print('Recognizing..')
                query = r.recognize_google(audio)
                print(f'Command {query}')
                query = query.lower()
                if 'alexa' in query:
                    query = query.replace('alexa', '')
                else:
                    query=''
                
            except Exception as e:
                #speak('Say that again please..')
                return 'none'
            
            return query

    @pyqtSlot()
    def run(self):
        print('run')
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
            on = True
            while on:
                self.query = self.take_command()

                if 'open notepad' in self.query:
                    speak('opening notepad')
                    npath = "F:\\Windows\\system32\\notepad.exe"
                    os.startfile(npath)
                elif 'open command prompt' in self.query:
                    os.system('start cmd')
                elif 'open camera' in self.query:
                    cap = cv2.VideoCapture(0)
                    while True:
                        ret, img = cap.read()
                        cv2.imshow('cam', img)
                        if k==27:
                            break
                        cap.release()
                        cv2.destroyAllWindow()
                elif 'play music' in self.query:
                    music_dir = 'F:\\Users\\Public\\Music\\Sample Music'
                    songs = os.listdir(music_dir)
                    #rd = random.choice(songs)
                    for song in songs:
                        if song.endswith('.mp3'):
                            os.startfile(os.path.join(music_dir, song))
                elif 'play video' in self.query:
                    video = self.query.split('video')[-1]
                    speak(('playing ' + video))
                    try:
                        pywhatkit.playonyt(video)
                    except:
                        None
                elif 'wikipedia' in self.query:
                    speak('searching wikipedia....')
                    query = query.replace('wikipedia', '')
                    results = wikipedia.summary(query, sentences=2)
                    speak(results)
                elif 'open youtube' in self.query:
                    webbrowser.open('youtube.com')
                elif 'open google' in self.query:
                    speak('shant do you wnat to search?')
                    cm = takecommand().lower()
                    webbrowser.open(f'{cm}')
                elif 'close notepad' in self.query:
                    speak('closing notepad')
                    os.system('taskkill /f /im notepad.exe')
                elif 'switch the window' in self.query:
                    pyautogui.keyDown('alt')
                    pyautogui.press('tab')
                    time.sleep(1)
                    pyautogui.keyUp('alt')
                elif 'tell me news' in self.query:
                    speak('feteching the lastest news')
                    news()
                elif 'search' in self.query:
                    speak('what do you want to know')
                    how = self.take_command()
                    try:
                        if 'exit' in how or 'close' in how or 'forget' in how:
                            speak('okay sir')
                        else:
                            max_results = 1
                            how_to = search_wikihow(how, max_results)
                            assert len(how_to) == 1
                            how_to[0].print()
                            speak(how_to[0].summary)
                    except Exception as e:
                        speak('sorry sir, i am not able to find this')
                elif 'where i am' in self.query or 'where we are' in self.query:
                    speak('let me check')
                    try:
                        ipAdd = requests.get('https://api.ipify.org/').text
                        print(idAdd)
                        url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
                        location = geocoder.ip(ipAdd)
                        print(location.city, pytz.country_names[location.country])
                    except Exception as e:
                        ipAdd = requests.get('https://api.ipify.org/').text
                        url = 'https://get.geojs.io/v1/ip/geo/'+ipAdd+'.json'
                        location = geocoder.ip(ipAdd)
                        speak(f'we are in {location.city}, in {pytz.country_names[location.country]}')
                elif 'take a screenshot' in self.query:
                    speak('please tell me the name for screeshot')
                    name = take_command().lower()
                    speak('please hold the screen for a few seconds')
                    time.sleep(3)
                    img = pyautogui.screenshot()
                    img.save(f'{name}.png')
                    speak(f'it is done, the {name} were save')
                elif 'management files' in self.query:
                    speak('what do you want to do')
                    condition = take_command().lower()
                    if 'hide' in condition:
                        os.system('attrib +h /s /d')
                        speak('all files now are hidden')
                    elif 'visible' in condition:
                        os.system('attrib -h /s /d')
                        speak('all files now are visible')
                    elif 'leave it' in condition or 'leave for now' in condition:
                        speak('leaving..')
                elif 'what time is it' in self.query:
                    time = datetime.datetime.now().strftime('%H:%M')
                    speak(('Now is ', time))
                elif 'weather' in self.query:
                    search = 'weather forecast'
                    url = f'https://google.com/search?q={search}'
                    r = requests.get(url)
                    data = BeautifulSoup(r.text, 'html.parser')
                    temp = data.find('div', class_='BNeawe').text
                    speak(f'current {search} is {temp} degrees')
                elif 'internet speed' in self.query:
                    import speedtest
                    st = speedtest.Speedtest()
                    dl = st.download()
                    up = st.upload
                    speak(f'sir in this moment we have {dl} of download and {up} of upload')
                elif 'more volume' in self.query:
                    pyautogui.press('volumeup')
                elif 'less volume' in self.query:
                    pyaoutgui.press('volumedown')
                elif 'mute volume' in self.query or 'unmute volume' in self.query:
                    pyautogui.press('volumemute')
                    speak('hello sir')
                elif 'goodbye' in self.query:
                    speak('thanks sir, have a good day')
                    on = False
                    
        except:
            # traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


# In[ ]:





# In[6]:


class MainWindow(QMainWindow):

# 2
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.counter = 0
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.movie = QtGui.QMovie("F:/Users/Eva/Pictures/Rehoboam.gif")
        self.ui.label.setMovie(self.ui.movie)
        self.ui.movie.start()
        layout = QVBoxLayout()
        self.l = QLabel("")
        b = QPushButton("GO!")
        b.pressed.connect(self.oh_no)
        layout.addWidget(self.l)
        layout.addWidget(b)

        w = QWidget()
        w.setLayout(layout)

        self.setCentralWidget(w)

        self.show()

        self.threadpool = QThreadPool() # 1
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

    def progress_fn(self, n):
        print("%d%% done" % n)

    def execute_this_fn(self, progress_callback):
        for n in range(0, 5):
            time.sleep(1)
            #progress_callback.emit(n*100/4)
            print('Loading... ', n*25)
        wish()
        return "Done."

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def oh_no(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn) # Any other args, kwargs are passed to the run function
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)


# In[ ]:


app = QApplication([])
window = MainWindow()
app.exec_()


# In[ ]:




