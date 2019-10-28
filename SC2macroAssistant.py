# base code from
# https://www.tutorialspoint.com/design-a-keylogger-in-python
# https://gist.github.com/jamesgeorge007/cb68fedd8419721f6f4c7a7643181974

from pynput.keyboard import Key, KeyCode, Listener
import numpy as np
# https://pypi.org/project/numpy_ringbuffer/ 
# doc https://github.com/eric-wieser/numpy_ringbuffer/blob/master/numpy_ringbuffer/__init__.py

import time
from timeloop import Timeloop # https://medium.com/greedygame-engineering/an-elegant-way-to-run-periodic-tasks-in-python-61b7c477b679
from datetime import timedelta

from playsound import playsound


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
# playsound('macroCycle.mp3') # https://youtu.be/f0chGt6IVBo?t=2964 49:24
# playsound('spendLarva.mp3') # https://youtu.be/O3aGlfvQiqo?t=217 3:37


scriptStart = time.time() # https://www.programiz.com/python-programming/time
lastMacroCycle = scriptStart
lastLarvaSpent = scriptStart

counter = 0
bufferSize = 3
lastActionsBuffer = []
tl = Timeloop()

# TODO 1 check for shift+insert = my inital GLHF thing, to unpause the scriptStart
# TODO 1 check for F10+n or F10+w or F10+s to stop the script
# TODO 1 use a flag is_working to set lastMacroCycle = time.time() and lastLarvaSpent= time.time()

# TODO 2 count hints per game (use TODO1) and store the counts in two CSV files, to track improvement.
# TODO 2 - count hints and store them in an ever growing file, to track players improvement. 

# TODO 3: in more columns: for larva and for injects!
# Csv:Datetime, gameDurationSeconds, gameDurationMinutes, larvaHints, injectHints, keysCount, larvaHPM, injectHPM, KPM
# Logger basicCofigdatefmt="%d.%m.%Y %H:%M" 
# Use the specified date/time format, as accepted by time.strftime()



@tl.job(interval=timedelta(seconds=1))
def checkMacro():
    print "1s job current time : {}".format(time.ctime())
    now = time.time()
    if lastMacroCycle+30 <= now: # lastCycle=30 // now=45 // now = 61
        playsound('macroCycle.mp3')
    
    if lastLarvaSpent+15 <= now: # lastlarva=30 // now=45 // now = 61
        playsound('spendLarva.mp3')
    
    
tl.start(block=False) # do not move this line

def checkPlayerActions(lastActionIndex):
    global lastMacroCycle, lastLarvaSpent
    
    # spam at the start of the game
    if (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('8') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('8') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('0')) \
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('0') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('0') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('8')): 
        lastMacroCycle = time.time()
        lastLarvaSpent= time.time()
        print ("So, you are spamming now?")
    
    # normal cycle or inital hotkey of new queen and inject 
    if (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == KeyCode.from_char('u') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('-') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == Key.shift_r) \
    or (lastActionsBuffer[(lastActionIndex+1)%bufferSize] == Key.ctrl \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('u') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('-')): # inital hotkey of new queen and inject 
        lastMacroCycle = time.time()
        print ("yay, an inject was detected!")

    if lastActionsBuffer[(lastActionIndex+1)%bufferSize]  == KeyCode.from_char('o') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('p') \
    and lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('j'): # opj = drones
        lastLarvaSpent= time.time()
        print ("yay, drones were made!")

    if lastActionsBuffer[(lastActionIndex+1)%bufferSize]  == KeyCode.from_char('o') \
    and lastActionsBuffer[(lastActionIndex+2)%bufferSize] == KeyCode.from_char('p') \
    and (lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('p')  # opp = lings
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char(';')  # op; = roach
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('[')  # op[ = hydra
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('h')  # oph = corruptor
    or lastActionsBuffer[(lastActionIndex+0)%bufferSize] == KeyCode.from_char('-') ): # op- = overlord
        lastLarvaSpent = time.time()
        print ("yay, army was made!")


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
