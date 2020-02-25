import microgear.client as microgear
import time
import logging
import random

appid = "raspicmru"
gearkey = "artG7aZBTy9CSwq"
gearsecret =  "D2VSe8wfb5S3IRjls3XOMmC1P"

microgear.create(gearkey,gearsecret,appid,{'debugmode': True})

def connection():
    logging.info("Now I am connected with netpie")

def subscription(topic,message):
    logging.info(topic+" "+message)

def disconnect():
    logging.debug("disconnect is work")

microgear.setalias("doraemon")
microgear.on_connect = connection
microgear.on_message = subscription
microgear.on_disconnect = disconnect
microgear.subscribe("/mails")
microgear.connect(False)

while True:
    if(microgear.connected):
        check = random.randint(1,100)
        #print(check)
        microgear.chat("check",check)
    time.sleep(5)