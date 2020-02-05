from threading import Thread
import RPi.GPIO as GPIO
import time

import pyrebase
import os
import pygame, sys
import pygame.image
from pygame.locals import *
import pygame.camera
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import cv2
import numpy as np
from pyfcm import FCMNotification
from datetime import datetime,timedelta,date

from time import strftime

config = {
  "apiKey": "AIzaSyBntX85ZOZ2SXLjZe7Ff3nMass9_rEPHQc",
  "authDomain": "fir-sample-ec94b.firebaseapp.com",
  "databaseURL": "https://fir-sample-ec94b.firebaseio.com",
  "storageBucket": "fir-sample-ec94b.appspot.com",
}

push_service = FCMNotification(api_key="AAAAChe61dw:APA91bFD-sByErGofjSVFneDtFtd8O7X1eyDo_xSONZ14TzLhMGjAbegk_lggXH4-5ALBdQFwJFi8JDGJ651MVgl8DkfefAmpUAtCNb7gquDwANfRZS9iOcMvO3JUJoJRP9cCiaHMu9P")
                    
firebase = pyrebase.initialize_app(config)
db = firebase.database()


SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

GPIO.setmode(GPIO.BCM)

pin_to_circuit = 22

gpio_1=26
gpio_2=24
gpio_3=20
gpio_4=12
gpio_light=14

SOIL = 2

cardcheck = "CARD3"


GPIO.setup(gpio_1, GPIO.OUT)
GPIO.setup(gpio_2, GPIO.OUT)
GPIO.setup(gpio_3, GPIO.OUT)
GPIO.setup(gpio_4, GPIO.OUT)
GPIO.setup(gpio_light, GPIO.OUT)




def ldr():
    while True:
        result = db.child(cardcheck).child("SET").get()        
        if result.val()==1:
            time.sleep(0.5)
            
            
            data = rc_time(pin_to_circuit)
            db.child(cardcheck).child("LIGHT").set(data)
            light = db.child(cardcheck).child("STATUS").child("LIGHT").get()
            
            open = db.child(cardcheck).child("SENSER").child("LIGHT").child("OPEN").get()
            close = db.child(cardcheck).child("SENSER").child("LIGHT").child("CLOSE").get()
            
            light = db.child(cardcheck).child("STATUS").child("LIGHT").get()        
            
            if light.val() == 0 :
 
                print("LDR 3 : ",rc_time(pin_to_circuit))
                
                if rc_time(pin_to_circuit) <= int(open.val()):
                    GPIO.output(gpio_light, False)
                if rc_time(pin_to_circuit) >= int(close.val()):
                    GPIO.output(gpio_light, True)
            
        
def soil():
    while True:
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            time.sleep(0.5)
            try:
                values1 = mcp.read_adc(SOIL)
                sum =  (values1*100)/1023

                #print (registration_id)
                print("SOIL 3 : ",values1)
                db.child(cardcheck).child("SOIL").set('%.0f'%sum)
                
                water = db.child(cardcheck).child("STATUS").child("WATER").get()
                compost = db.child(cardcheck).child("STATUS").child("COMPOST").get()
                
                            
                opens = db.child(cardcheck).child("SENSER").child("LIGHT").child("OPEN").get()
                closes = db.child(cardcheck).child("SENSER").child("LIGHT").child("CLOSE").get()
                check = db.child("CHECK").child("CHECKWATER").get()   
                

                if check.val()==0:
                    if water.val() == 0:
                        if compost.val() == 0:
                            if values1 <= int(opens.val()):
                                GPIO.output(gpio_1, False)
                                GPIO.output(gpio_2, False)
                                GPIO.output(gpio_4, False)
                            if values1 >= int(closes.val()):
                                GPIO.output(gpio_1, True)
                                GPIO.output(gpio_2, True)
                                GPIO.output(gpio_4, True)
                        else:                
                            GPIO.output(gpio_1, False)
                            GPIO.output(gpio_4, False)
                            GPIO.output(gpio_2, True)
            except:
                soil()

def compost():
    while True:
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            time.sleep(0.5)

            HH = db.child(cardcheck).child("TIMEGROW").child("H").get()
            MM = db.child(cardcheck).child("TIMEGROW").child("M").get()
            water = db.child(cardcheck).child("STATUS").child("WATER").get()
            
            #cha = str(HH.val())+':'+str(MM.val())+':0'            
            #datetime_object = datetime.strptime(cha, '%H:%M:%S')
            #newdate = datetime.strftime(datetime_object,'%H:%M:%S')
            
            cha = str(HH.val())+':'+str(MM.val())            
            datetime_object = datetime.strptime(cha, '%H:%M')
            newdate = datetime.strftime(datetime_object,'%H:%M')
            
            
            te = datetime.now()
            datecheck = te.strftime("%H:%M:%S")
            
            compost = db.child(cardcheck).child("STATUS").child("COMPOST").get()
            check = db.child("CHECK").child("CHECKWATER").get()           

            if check.val()==0:
                if compost.val() == 0:
                    #db.child(cardcheck).child("STATUS").child("WATER").set(0)
                    if water.val() == 0:
                        if newdate==datecheck:
                            GPIO.output(gpio_1, False)
                            GPIO.output(gpio_3, False)
                            GPIO.output(gpio_4, False)
                            time.sleep(1)
                        else:
                            GPIO.output(gpio_1, True)
                            GPIO.output(gpio_3, True)
                            GPIO.output(gpio_4, True)
                else:                
                    GPIO.output(gpio_1, False)
                    GPIO.output(gpio_3, False)
                    GPIO.output(gpio_4, False)
                
def cam():
    result = db.child(cardcheck).child("SET").get()
    while True:
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            te = datetime.now()
            hh = int(te.strftime("%H"))
            mm = te.strftime("%M")
            ss = te.strftime("%S")
            datecheck = te.strftime("%d/%m/%Y")
            dated = te.strftime("%Y/%m/%d")
            times = te.strftime("%H:%M:%S")
            
            #if hh%8==0 and mm == '00' and ss == '00':
            if hh%8==0 and mm == '00':
                width = 640
                height = 480

                pygame.init()
                pygame.camera.init()
                camlist = pygame.camera.list_cameras()
                cam = pygame.camera.Camera(camlist[2],(width,height))
                #cam = pygame.camera.Camera("/dev/video0",(width,height))
                cam.start()

                image = cam.get_image()    
                pygame.image.save(image,'picture3.jpg')
                cam.stop()
                storage = firebase.storage()
                storage.child("picture").child("picture3.jpg").put("picture3.jpg")
                #time.sleep(1)
                time.sleep(60)
       
def date():
    while True:
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            te = datetime.now()
            hh = int(te.strftime("%H"))
            mm = te.strftime("%M")
            ss = te.strftime("%S")
            
            notify = db.child(cardcheck).child("NOTFY").get()
            day = db.child(cardcheck).child("DAYGROW").child("DAY").get()
            month = db.child(cardcheck).child("DAYGROW").child("MONTH").get()
            year = db.child(cardcheck).child("DAYGROW").child("YEAR").get()
            startdate = str(day.val())+"/"+str(month.val())+"/"+str(year.val())
            date = datetime.strptime(startdate,"%d/%m/%Y")
            print("daygrow 1 : ",date)
                
            now = datetime.now()
                
            dayStart=now.day
            dayEnd=date.day
            resultday = now-date
                
            #db.child(cardcheck).update({"DATE": resultday.days})
            db.child(cardcheck).child("DATE").set(resultday.days)
                
            set = date + timedelta(days=40)          
            newdate = datetime.strftime(set,"%d/%m/%Y")
            d1 = now.strftime("%d/%m/%Y")
            if hh%8==0 and mm == '00':    
                if newdate == d1:
                    if notify.val()==0:
                        push_service = FCMNotification(api_key="AAAAChe61dw:APA91bFD-sByErGofjSVFneDtFtd8O7X1eyDo_xSONZ14TzLhMGjAbegk_lggXH4-5ALBdQFwJFi8JDGJ651MVgl8DkfefAmpUAtCNb7gquDwANfRZS9iOcMvO3JUJoJRP9cCiaHMu9P")
                        token = db.child("Token").get()
                        registration_id = token.val()
                        message_title = "แจ้งเตือนแปลง3"
                        message_body = "ใกล้วันเก็บเกี่ยวแล้ว"
                        result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
                        print(result)
                        db.child(cardcheck).child("NOTFY").set(1)
                        time.sleep(60)
                else:
                    db.child(cardcheck).child("NOTFY").set(0)
    
    
def savedb():    
    while True:
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            te = datetime.now()
            hh = int(te.strftime("%H"))
            mm = te.strftime("%M")
            ss = te.strftime("%S")
            datecheck = te.strftime("%d/%m/%Y")
            dated = te.strftime("%Y/%m/%d")
            times = te.strftime("%H:%M:%S")
            
            light = db.child(cardcheck).child("LIGHT").get()
            soil = db.child(cardcheck).child("SOIL").get()
            name = db.child(cardcheck).child("NAME").get()
            
            day = db.child(cardcheck).child("DAYGROW").child("DAY").get()
            month = db.child(cardcheck).child("DAYGROW").child("MONTH").get()
            year = db.child(cardcheck).child("DAYGROW").child("YEAR").get()
            name = db.child(cardcheck).child("NAME").get()
            grow = db.child(cardcheck).child("GROW").get() 
            
                       
            if hh%3==0 and mm == '00':
            #if hh%3==0 and mm == '00' and ss == '00':
                data = {"LIGHT": light.val(),
                "SOIL" : soil.val(),
                "DATE": datecheck,
                "TIME": times,
                "GROW" : grow.val(),}
                db.child(cardcheck).child("DATA").push(data)
                db.child("DB").child(year.val()).child(month.val()).child(day.val()).child(name.val()).push(1)
                #ขาดค่าดีเทค
                #db.child("DB").child(name.val()).child(datecheck).push(data)
                #time.sleep(1)
                time.sleep(60)
    
def onetime():
    while True:
        photo = db.child(cardcheck).child("PHOTO").get()
        light = db.child(cardcheck).child("STATUS").child("LIGHT").get()
        compost = db.child(cardcheck).child("STATUS").child("COMPOST").get()
        water = db.child(cardcheck).child("STATUS").child("WATER").get()
        result = db.child(cardcheck).child("SET").get()
        if result.val()==1:
            if photo.val() == 1:
                width = 640
                height = 480

                pygame.init()
                pygame.camera.init()
                camlist = pygame.camera.list_cameras()
                cam = pygame.camera.Camera(camlist[2],(width,height))
                cam.start()

                image = cam.get_image()    
                pygame.image.save(image,'picture3.jpg')
                cam.stop()
                storage = firebase.storage()
                storage.child("picture").child("picture3.jpg").put("picture3.jpg")
                db.child(cardcheck).child("PHOTO").set(0)
                
            if light.val() == 1:
                GPIO.output(gpio_light, False)
            if compost.val() == 1:
                GPIO.output(gpio_1, False)
                GPIO.output(gpio_3, False)
                GPIO.output(gpio_4, False)
                
            if water.val() == 1:
                GPIO.output(gpio_1, False)
                GPIO.output(gpio_2, False)
                GPIO.output(gpio_4, False)

            
def detect():
    while True:
        te = datetime.now()
        hh = int(te.strftime("%H"))
        mm = te.strftime("%M")
        result = db.child(cardcheck).child("SET").get()
        modeGrow = db.child(cardcheck).child("RESULT").get()
        notify = db.child(cardcheck).child("NOTFY").get()
        if result.val()==1:
            if modeGrow.val()==1:
                frame = cv2.imread('picture3.jpg')
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv_channels = cv2.split(hsv)

                rows = frame.shape[0]
                cols = frame.shape[1]

                for i in range(0, rows):
                    for j in range(0, cols):
                        h = hsv_channels[0][i][j]

                        if h > 30 and h < 90:
                            hsv_channels[2][i][j] = 255
                        else:
                            hsv_channels[2][i][j] = 0



                height, width = hsv_channels[2].shape
                count = cv2.countNonZero(hsv_channels[2])
                size = hsv_channels[2].size

                cal=(count/size)*100
                #print('%.0f'%cal)
                #print('Detect color 1 %.0f'%cal)
                db.child(cardcheck).child("GROW").set('%.0f'%cal)
                check = '%.0f'%cal
                if hh%3==0 and mm == '00':
                    if int(check) >= 80:
                        if notify.val()==0:
                            push_service = FCMNotification(api_key="AAAAChe61dw:APA91bFD-sByErGofjSVFneDtFtd8O7X1eyDo_xSONZ14TzLhMGjAbegk_lggXH4-5ALBdQFwJFi8JDGJ651MVgl8DkfefAmpUAtCNb7gquDwANfRZS9iOcMvO3JUJoJRP9cCiaHMu9P")
                            token = db.child("Token").get()
                            registration_id = token.val()
                            message_title = "แจ้งเตือนแปลง3"
                            message_body = "ใกล้เก็บเกี่ยวได้แล้ว"
                            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
                            print(result)
                            db.child(cardcheck).child("NOTFY").set(1)
                            time.sleep(60)
                            
                    else:
                        db.child(cardcheck).child("NOTFY").set(0)
                    
                #print (check)

            else:
            
                image = cv2.imread("picture3.jpg")

                hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

                weaker = np.array([0,0,100])
                stronger = np.array([10,255,255])

                mask = cv2.inRange(hsv, weaker, stronger)
                contours, hierarchy= cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                cv2.drawContours(image, contours, -1, (0,255,0), 3)

                threshold_area = 10000
                count = 0

                for cnt in contours:        
                    area = cv2.contourArea(cnt)         
                    if area > threshold_area:                   
                         count = count+1
                if hh%3==0 and mm == '00': 
                    if count >= 1:
                        if notify.val()==0:
                            push_service = FCMNotification(api_key="AAAAChe61dw:APA91bFD-sByErGofjSVFneDtFtd8O7X1eyDo_xSONZ14TzLhMGjAbegk_lggXH4-5ALBdQFwJFi8JDGJ651MVgl8DkfefAmpUAtCNb7gquDwANfRZS9iOcMvO3JUJoJRP9cCiaHMu9P")
                            token = db.child("Token").get()
                            registration_id = token.val()
                            message_title = "แจ้งเตือนแปลง3"
                            message_body = "ใกล้เก็บเกี่ยวได้แล้ว"
                            result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
                            print(result)
                            db.child(cardcheck).child("NOTFY").set(1)
                            time.sleep(60)
                            
                    else:
                        db.child(cardcheck).child("NOTFY").set(0)
               
                #print('detect count 1 :',count)  
                db.child(cardcheck).child("GROW").set(count)
                
    
    
def rc_time (pin_to_circuit):
    count = 0
  
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)

    GPIO.setup(pin_to_circuit, GPIO.IN)

    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1

    return count

    
if __name__ == '__main__':
    Thread(target = ldr).start()
    Thread(target = soil).start()
    Thread(target = cam).start()
    Thread(target = date).start()
    Thread(target = savedb).start()
    Thread(target = onetime).start()
    Thread(target = compost).start()
    Thread(target = detect).start()
