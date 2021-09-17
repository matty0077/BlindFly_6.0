#!/usr/bin/env python
import sys, time
import threading
import math
from grove.gpio import GPIO
from grove.adc import ADC

usleep = lambda x: time.sleep(x / 1000000.0)
_TIMEOUT1 = 1000
_TIMEOUT2 = 10000

#############################SOUNDFX
def soundplay(folder, fx, vol):
    import pygame
    FXPATH="/home/pi/Desktop/BlindFly_6.0/BlindFly_Base/FX/"
    pygame.mixer.init()
    pygame.mixer.music.set_volume(vol)#put above?
    pygame.mixer.music.load(FXPATH + folder +'/' + fx + ".wav")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy==True:
        continue
#soundplay("ranger","far",.1)
    
########################THREADER
def Threader(action):
    THREAD=threading.Thread(target=action)
    #Thread.daemon=True
    THREAD.start()
    THREAD.join()#optional?

######################SHUTDOWN MACHINE
def ShutDown():
    import os
    soundplay("meta","shut_off",.5)
    time.sleep(2)
    os.system("sudo shutdown now -P")
    
########################################ROTARY ANGLE SENSOR  CLASS
class GroveRotaryAngleSensor(ADC):
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
    
    @property
    def value(self):
        return self.adc.read(self.channel)
    
############################################ULTRASONIC RANGER CLASS
class GroveUltrasonicRanger(object):
    def __init__(self, pin):
        self.dio = GPIO(pin)

    def _get_distance(self):
        self.dio.dir(GPIO.OUT)
        self.dio.write(0)
        usleep(2)
        self.dio.write(1)
        usleep(10)
        self.dio.write(0)
        self.dio.dir(GPIO.IN)

        t0 = time.time()
        count = 0
        while count < _TIMEOUT1:
            if self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT1:
            return None

        t1 = time.time()
        count = 0
        while count < _TIMEOUT2:
            if not self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT2:
            return None

        t2 = time.time()
        dt = int((t1 - t0) * 1000000)
        if dt > 530:
            return None

        distance = ((t2 - t1) * 1000000 / 29 / 2)    # cm
        return distance

    def get_distance(self):
        while True:
            dist = self._get_distance()
            if dist:
                return dist

#Grove = GroveUltrasonicRanger
#Grove = GroveRotaryAngleSensor
            
##########################READ DISTANCE
def Distancer():
    try:
        pin = 5
        sonic = GroveUltrasonicRanger(pin)
        ROTT = GroveRotaryAngleSensor(0)
        TEMPO=ROTT.value*.001#turns angle of sensor into decimal to control response time
        #
        ROTTV = GroveRotaryAngleSensor(2)
        TEMPOV=ROTTV.value*.0007#turns angle of sensor into decimal to control response time
        #
        ####################far range
        if sonic.get_distance()<=1000 and sonic.get_distance()>750:
            time.sleep(2+TEMPO)
            #soundplay("ranger","far",.1)
            soundplay("ranger","far",TEMPOV)
            
        ##################MEDIUM RANGES
        elif sonic.get_distance()<=750 and sonic.get_distance()>500:
                time.sleep(1.75+TEMPO)
                #soundplay("ranger","med",.2)
                soundplay("ranger","med",TEMPOV)

        elif sonic.get_distance()<=500 and sonic.get_distance()>350:
                time.sleep(1.25+TEMPO)
                #soundplay("ranger","med1",.3)
                soundplay("ranger","med1",TEMPOV)

        elif sonic.get_distance()<=350 and sonic.get_distance()>250:
                time.sleep(1+TEMPO)
                #soundplay("ranger","med2",.5)
                soundplay("ranger","med2",TEMPOV)

        #############close ranges
        elif sonic.get_distance()<=250 and sonic.get_distance()>150:
                time.sleep(.75+TEMPO)
                #soundplay("ranger","close",.7)
                soundplay("ranger","close",TEMPOV)     

        elif sonic.get_distance()<=150 and sonic.get_distance()>75:
            time.sleep(.5+TEMPO)
            #soundplay("ranger","close1",.9)
            soundplay("ranger","close1",TEMPOV)

        elif sonic.get_distance()<=75 and sonic.get_distance()>5:
            time.sleep(.25+TEMPO)
            #soundplay("ranger","close2",1.0)
            soundplay("ranger","close2",TEMPOV)
            
        ################SHUT DOWN
        elif sonic.get_distance()<=1:
            ShutDown()

        #print('{} cm'.format(sonic.get_distance()))

    except KeyboardInterrupt:
        soundplay("meta","exit",.5)
        print("Pogram Exit")
        time.sleep(1)
        sys.exit()
    except IOError:
        soundplay("meta","error2",.5)
        print ("Error")
        time.sleep(1)
        sys.exit()
            
#########
soundplay("meta","connected",.5)
time.sleep(1.5)
while True:
    Distancer()
