# base code from
# https://www.tutorialspoint.com/design-a-keylogger-in-python
# https://gist.github.com/jamesgeorge007/cb68fedd8419721f6f4c7a7643181974

from pynput.keyboard import Key, KeyCode, Listener, Controller # https://pythonhosted.org/pynput/keyboard.html
import numpy as np
# https://pypi.org/project/numpy_ringbuffer/ 
# doc https://github.com/eric-wieser/numpy_ringbuffer/blob/master/numpy_ringbuffer/__init__.py

import time
from timeloop import Timeloop # https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679
from datetime import timedelta

from playsound import playsound # Windows users
from pygame import mixer # linux people; https://stackoverflow.com/a/56621821

import logging
from threading import Thread
import locale


'''
I use the core 2.0 so my hotkeys are as follows:

 u - inject queen hotkey (use 5 on standard layout)
 - - inject ability for queen (use V on standard layout)
 o - all hatcheries (use 4 on standard layout)
 p - select all larva button (use S on standard layout)
 p - lings hotkey (use Z on standard layout)
 ; - roach hotkey (use R on standard layout)
 [ - hydra hotkey (use H on standard layout)
 h - corruptor hotkey (use C on standard layout)
'''

# cmd.exe /K "cd C:\Users\Teacher\Documents\StarCraft II\MacroAssistant == start shell in specific folder


scriptStart = time.time() # https://www.programiz.com/python-programming/time
lastMacroCycle = scriptStart
lastLarvaSpent = scriptStart
counter = 0
larvaHints = 0 # count hints to track players improvement.
larvaHints = 0
injectHints = 0
larvaHintsPeriod = 15
injectHintsPeriod = 60
larvaRuleDimsScreen = True # every player must lose a finger if he breaks the larva rule.

is_in_game = False

bufferSize = 3
lastActionsBuffer = []
tl = Timeloop()


# setup logger for this program only, as timeloop tends to spam in the logs
formatter = logging.Formatter(fmt='%(asctime)s, %(message)s', datefmt="%d.%m.%Y %H:%M")
handler = logging.FileHandler("AI_Coaching.csv")        
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
keyboard = Controller() # https://nitratine.net/blog/post/simulate-keypresses-in-python/



print("Hello, my name is Larry Crojerg, larva and macro injecting AI coach for zerg. ") 

mixer.init()


def soundEffect(filename, blocking = True):
    #playsound(filename)
    
    mixer.music.load(filename)
    mixer.music.play()
    while mixer.music.get_busy() == True:
        continue
    
    if blocking:
        pass
        # TODO research more how to play parallel sounds in pygame
        #oggSound = mixer.Sound("a.ogg")
        #mixer.Sound.play(oggSound)
        #sleep(5)
        #larvaSound = mixer.Sound('spendLarva.mp3')
        #ggSound = mixer.Sound("gg.mp3")
        #macroSound = mixer.Sound("macroCycle.mp3")
        #diamondSound = mixer.Sound("diamond x2.mp3")
        #diamondSound.play()
    else:   
        pass
        #mixer.music.load(filename)
        #mixer.music.play()




### TODO research more how to play parallel sounds in pygame
#soundEffect('spendLarva.mp3')
#soundEffect("gg.mp3", blocking=False)
#soundEffect('spendLarva.mp3')

    
def interruptPlayer():
    # stop sound effects
    keyboard.press(Key.f11)
    keyboard.release(Key.f11)
    # stop music
    keyboard.press(Key.f12)
    keyboard.release(Key.f12)
    
    # dim the screen 5 steps
    for i in range(21): 
        keyboard.press(Key.alt)
        keyboard.press(Key.page_down)
        keyboard.release(Key.page_down)
        keyboard.release(Key.alt)
        time.sleep(0.1)
    
    time.sleep(5)
    
    # restore screen brightness
    for i in range(21): 
        keyboard.press(Key.alt)
        keyboard.press(Key.page_up)
        keyboard.release(Key.page_up)
        keyboard.release(Key.alt)
        time.sleep(0.1)
    
    # resume sound effects
    keyboard.press(Key.f11)
    keyboard.release(Key.f11)
    # resume music
    keyboard.press(Key.f12)
    keyboard.release(Key.f12)
    
    
    
    
@tl.job(interval=timedelta(seconds=1))
def checkMacro():
    print("1s job current time : {}".format(time.ctime()))
    global injectHints, larvaHints
    
    if is_in_game:
        now = time.time()
        if lastMacroCycle+injectHintsPeriod <= now: # lastCycle=30 // now=45 // now = 61
            # count hints to track players improvement.
            injectHints = injectHints + 1 # TODO dont count the same hint too many times, wait for the player to execute it before you count again
            soundEffect('macroCycle.mp3') # https://youtu.be/f0chGt6IVBo?t=2964 49:24
            
        if lastLarvaSpent+larvaHintsPeriod <= now: # lastlarva=30 // now=45 // now = 61
            # count hints to track players improvement.
            larvaHints = larvaHints + 1 # TODO dont count the same hint too many times, wait for the player to execute it before you count again
            soundEffect('spendLarva.mp3') # https://youtu.be/O3aGlfvQiqo?t=217 3:37
            if larvaRuleDimsScreen:
                interruptPlayer()   

    
tl.start(block=False) # do not move this line

def storeStatsInFile():
    # count hints and store them in an ever growing file, to track players improvement
    # in many columns: for larva and for injects!
    
    global counter, larvaHints, injectHints, scriptStart
    # Csv: Datetime, gameDurationSeconds, gameDurationMinutes, larvaHints, injectHints, keysCount, larvaHPM, injectHPM, KPM
    scriptEnd = time.time()
    gameDurationSeconds = scriptEnd - scriptStart
    gameDurationMinutes = "%02d:%02d" % (gameDurationSeconds/60, gameDurationSeconds%60)
    keysCount = counter
    
    larvaHPM = (larvaHints/gameDurationSeconds) * 60
    injectHPM = (injectHints/gameDurationSeconds) * 60
    KPM = (counter/gameDurationSeconds) * 60
    
    #locale.setlocale(locale.LC_NUMERIC, 'Bulgarian') # 32 757 121,33
    larvaHPM_str = locale.format_string("%.2f", larvaHPM)
    injectHPM_str = locale.format_string("%.2f", injectHPM)
    
    # SQ = input("What was your SQ that game? ") # deprecated idea, can't force that input, and may break next game
    SQ = "??"
    # print("%d:%02d, %.2f" % (3, 3, 3.141516)) # 3:03, 3.14
    
    csvLine = "%d, %s, %d, %d, %d, \"%s\", \"%s\", %d, %s" % (gameDurationSeconds, gameDurationMinutes, larvaHints, injectHints, keysCount, larvaHPM_str, injectHPM_str, KPM, SQ)
    print("csvLine = " + csvLine)
    logger.info(csvLine)

def checkPlayerActions(lastActionIndex):
    global lastMacroCycle, lastLarvaSpent
    global counter, is_in_game, larvaHints, injectHints, scriptStart
    
    # check for shift+insert = my inital GLHF thing, to unpause the script
    if (lastActionsBuffer[(lastActionIndex-1)%bufferSize] == Key.shift_r \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == Key.insert): 
        
        scriptStart = time.time()
        lastMacroCycle = scriptStart
        lastLarvaSpent = scriptStart
        counter = 0
        larvaHints = 0 
        larvaHints = 0
        injectHints = 0
        
        is_in_game = True
        print("GL HF to you, too!")
        soundEffect("diamond x2.mp3", blocking=False)
        
    # check for F10+n or F10+w or F10+s to stop the script
    if (lastActionsBuffer[(lastActionIndex-1)%bufferSize] == Key.f10 \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('n')) \
    or (lastActionsBuffer[(lastActionIndex-1)%bufferSize] == Key.f10 \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('w')) \
    or (lastActionsBuffer[(lastActionIndex-1)%bufferSize] == Key.f10 \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('s')): 
        is_in_game = False
        print("Geeee Geeee!")
        soundEffect("gg.mp3", blocking=False)
        storeStatsInFile() # count hints and store them in an ever growing file, to track players improvement.
    
    # spam at the start of the game
    if (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('8') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('8') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('0')) \
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('0') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('0') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('8')): 
        lastMacroCycle = time.time()
        lastLarvaSpent= time.time()
        print("So, you are spamming now?")
    
    # normal cycle or inital hotkey of new queen and inject 
    if (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('u') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('-') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == Key.shift_r) \
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == Key.ctrl_r \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('u') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('-')) \
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('-') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == Key.ctrl_r \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('u'))\
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == Key.ctrl_r \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == Key.ctrl_r \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('u')): # inital hotkey of new queen and inject 
        lastMacroCycle = time.time()
        print("yay, an inject was detected!")

    if lastActionsBuffer[(lastActionIndex+1)%bufferSize]  == KeyCode.from_char('o') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('p') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('j'): # opj = drones
        lastLarvaSpent= time.time()
        print("yay, drones were made!")

    if lastActionsBuffer[(lastActionIndex+1)%bufferSize]  == KeyCode.from_char('o') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('p') \
    and (lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('p')  # opp = lings
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char(';')  # op; = roach
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('[')  # op[ = hydra
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('h')  # oph = corruptor
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('-') ): # op- = overlord
        lastLarvaSpent = time.time()
        print("yay, army was made!")


def keypress(key):
    global counter, lastActionsBuffer, bufferSize
    if counter == 0: 
        lastActionsBuffer = [key, key, key]
    
    lastActionsBuffer[counter%bufferSize] = key
    checkPlayerActions(counter%bufferSize)
    print(np.array(lastActionsBuffer))
    # lastActionsBuffer.append(key)
    
    counter = counter + 1
    
with Listener(on_press = keypress) as listener:
        listener.join()
