#setup scale declination and offsets for the collected data to calibrate the sensor

import RPi.GPIO as GPIO
import smbus
import time
import math
import csv

rev = GPIO.RPI_REVISION
if rev == 2 or rev == 3:
    bus = smbus.SMBus(1)
else:
    bus = smbus.SMBus(0)

address = 0x1e

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)
    
if __name__ == "__main__":
    write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
    write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
    write_byte(2, 0b00000000) # Continuous sampling

    scale = 0.92              # Set scale of 0.92
    
    minx = 0
    maxx = 0
    miny = 0
    maxy = 0

    for i in range(0,500):
        x_out = read_word_2c(3)
        y_out = read_word_2c(7)
        z_out = read_word_2c(5)
        
        
        if x_out < minx:
            minx=x_out
        
        if y_out < miny:
            miny=y_out
        
        if x_out > maxx:
            maxx=x_out
        
        if y_out > maxy:
            maxy=y_out

        time.sleep(0.1)

    print( "x offset: ", (maxx + minx) / 2) # Calculate x offset
    print( "y offset: ", (maxy + miny) / 2) # Calculate y offset
 
    x_offset = (maxx + minx) / 2
    y_offset = (maxy + miny) / 2

    x_out = (read_word_2c(3) - x_offset) * scale #x output after scaled
    y_out = (read_word_2c(7) - y_offset) * scale #y output after scaled
    z_out = (read_word_2c(5)) * scale            #z output after scaled

    bearing  = math.atan2(y_out, x_out) 
    if (bearing < 0):
        bearing += 2 * math.pi
    
    declination = 0.16              #declination angle at London
    bearing = math.degrees(bearing) + declination # Bearing after scaled
        
    print ("Bearing: ", bearing)
