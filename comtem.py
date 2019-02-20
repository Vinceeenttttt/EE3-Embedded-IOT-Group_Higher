import smbus		#import SMBus module of I2C
from time import sleep  #import sleep
import time
import json
import math
import paho.mqtt.client as mqtt

#setup for compass sensor
#some MPU6050 Registers and their Address
Register_A     = 0              #Address of Configuration register A
Register_B     = 0x01           #Address of configuration register B
Register_mode  = 0x02           #Address of mode register

X_axis_H    = 0x03              #Address of X-axis MSB data register
Z_axis_H    = 0x05              #Address of Z-axis MSB data register
Y_axis_H    = 0x07              #Address of Y-axis MSB data register
declination = -0.00669          #define declination angle of location where measurement going to be done
pi          = 3.14159265359     #define pi value
p = q = w = 0                   #define parameters used for determining the final result

client = mqtt.Client()
client.connect("ee-estott-octo.ee.ic.ac.uk",port=1883) #connect with the broker

def Magnetometer_Init():
        #write to Configuration Register A
        bus.write_byte_data(Device_Address, Register_A, 0x70)

        #Write to Configuration Register B for gain
        bus.write_byte_data(Device_Address, Register_B, 0xa0)

        #Write to mode Register for selecting mode
        bus.write_byte_data(Device_Address, Register_mode, 0)
	
def read_raw_data(addr):
    
        #Read raw 16-bit value
        high = bus.read_byte_data(Device_Address, addr)
        low = bus.read_byte_data(Device_Address, addr+1)

        #concatenate higher and lower value
        value = ((high << 8) | low)

        #to get signed value from module
        if(value > 32768):
            value = value - 65536
        return value


bus = smbus.SMBus(1) 	# or bus = smbus.SMBus(0) for older version boards
Device_Address = 0x1e   # HMC5883L magnetometer device address

Magnetometer_Init()     # initialize HMC5883L magnetometer 

print (" Reading Heading Angle")

while True:
    
	
        #Read Accelerometer raw value
        x = read_raw_data(X_axis_H)
        z = read_raw_data(Z_axis_H)
        y = read_raw_data(Y_axis_H)
        d = abs(x-p) + abs(z-q) + abs(w-y)        #define total declining angle of the sensor
        p = x
        q = z
        w = y
        if(d > 150):             #define threshold of the total angle above which a warning message will be sent
        	e = 1            #output to the user interface as a warning message
        else:
        	e = 0            #output to the user interface as a safe message
        print ("X reading is = %d°" %x)
        print ("Y reading is = %d°" %y)
        print ("Z reading is = %d°" %z)
        print ("d reading is = %d"  %d)
        heading = math.atan2(y, x) + declination
        
        #Due to declination check for >360 degree
        if(heading > 2*pi):
                heading = heading - 2*pi

        #check for sign
        if(heading < 0):
                heading = heading + 2*pi

        #convert into angle
        heading_angle = int(heading * 180/pi)    #heading angle can be used as a reference object to North
                                                 #though it will not be shown to the user interface

        a = json.dumps(e)                          #convert to json message
        client.publish("IC.embedded/HIGHER/com",a) #publish to the broker

        print(a)

        sleep(0.3)

        #setup for temperature&humidity sensor
        #SI7021 address, 0x40(64)
        #0xF5(245)   Select Relative Humidity NO HOLD master mode
        bus.write_byte(0x40, 0xF5)

        sleep(0.3)

        #SI7021 address, 0x40(64)
        #Read data back, 2 bytes, Humidity MSB first
        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        #convert the data
        humidity = ((data0 * 256 + data1) * 125 / 65536.0) - 6
        humround = round(humidity, 1)             #rounded to 1 decimal digit 

        sleep(0.3)

        #SI7021 address, 0x40(64)
        #0xF3(243)   Select temperature NO HOLD master mode
        bus.write_byte(0x40, 0xF3)

        sleep(0.3)

        #SI7021 address, 0x40(64)
        #read data back, 2 bytes, Temperature MSB first
        data0 = bus.read_byte(0x40)
        data1 = bus.read_byte(0x40)

        #convert the data
        cTemp = ((data0 * 256 + data1) * 175.72 / 65536.0) - 46.85
        cTempround = round(cTemp, 1)            #rounded to 1 decimal digit

        b = json.dumps(humround)
        client.publish("IC.embedded/HIGHER/hum",b+"%")

        c = json.dumps(cTempround)
        client.publish("IC.embedded/HIGHER/tem",c+chr(176)+"C")

        #output data to screen
        print ("Relative Humidity is : %.2f %%" %humidity)
        print ("Temperature in Celsius is : %.2f C" %cTemp)
