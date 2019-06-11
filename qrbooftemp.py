#!/usr/bin/python3
import numpy as np
import pyboof as pb
import os
from picamera import PiCamera
from time import sleep
import time

from datetime import datetime
import psycopg2


start = time.time()

#camera taking the picture 
camera = PiCamera()
print(datetime.now())#this output is for the logfile
#camera.resolution = (2592, 1944)
camera.resolution = (3280, 2464)
#camera.shutter_speed=4000
camera.capture('/home/pi/Desktop/capture.jpg')# saving picture 
camera.close()

#pyboof 


pb.init_memmap()

gray = pb.load_single_band('/home/pi/Desktop/capture.jpg', np.uint8)# loading the picture
detector = pb.FactoryFiducial(np.uint8).qrcode()#qrcode detecting
detector.detect(gray)

values ='' #create empty string

response = detector.detections
for qr in response:
   values += '{} '.format(qr.message)

print(values)#this output is for the logfile
print(len(response))#this output is for the logfile


#temperature
#the sensor adresse needs to be matched to the one of the sensor connected
sensor = '/sys/bus/w1/devices/28-01144058eeaa/w1_slave'
f= open(sensor, 'r')
content = f.read()
f.close()
stringvalue = content.split("\n")[1].split(" ")[9]
temperature = float(stringvalue[2:]) / 1000
print(temperature)#this ouptut is for the logfile


#passes results on to database
#the connection setup needs to be matched to your PostgreSQL database setup
try:
       connection = psycopg2.connect(user="username",#change to your user name
                                       password="password",#change to your password
                                       host="host",#change to your host
                                       database="database",#change to your database
                                       port="5432")#change to your port if necessary
       cursor = connection.cursor()

       command = ("""INSERT INTO qrcode(qrcode_id, ts, temp) VALUES (%s,%s,%s)""")#change table name if necessary
       record = (values, datetime.now(), temperature)
       cursor.execute(command, record)
       connection.commit()

       print( "Record inserted successfully into table")
except (Exception, psycopg2.Error) as error:
       if(connection):
               print("Failed to insert record into table", error)
finally:
       #closing db connection
       if(connection):
               cursor.close()
               connection.close()
               print("PostgreSQL connection is closed")
#saving the picture in the scan folder with its date and time
os.rename("/home/pi/Desktop/capture.jpg","/home/pi/Desktop/scan/scan{:_%d_%m_%Y_%H_%M_%S}.jpg".format(datetime.now()))
end = time.time()
print(end-start)#this output is for the logfile
