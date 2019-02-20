# Gather 500 readings and writes values to a CSV file which can easily be imported into Excel and be plotted in a scattered graph.
# Data collected while the bot is turned back and forwards through 360 degrees
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

compassValuesList = []
    
if __name__ == "__main__":
    write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
    write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
    write_byte(2, 0b00000000) # Continuous sampling

    scale = 0.92
   
    for i in range(0,500):
        x_out = read_word_2c(3)
        y_out = read_word_2c(7)
        z_out = read_word_2c(5)
        
        x_out_scaled = x_out * scale
        y_out_scaled = y_out * scale

        bearing  = math.atan2(y_out, x_out) 
        if (bearing < 0):
            bearing += 2 * math.pi
        bearing = math.degrees(bearing)
        
        print x_out, y_out, x_out_scaled, y_out_scaled, bearing
        
        compassValues = {}
        compassValues[ "X" ] = x_out
        compassValues[ "Y" ] = x_out
        compassValues[ "X_scaled" ] = x_out_scaled
        compassValues[ "Y_scaled" ] = y_out_scaled
        compassValues[ "Bearing" ] = bearing
        compassValuesList.append( compassValues )

        time.sleep(0.1)

    outputFilename = "Compass_values_{0}.csv".format( int( time.time() ) )
    with open( outputFilename, "w" ) as csvFile:
        dictWriter = csv.DictWriter ( csvFile,[ "X", "Y", "X_scaled", "Y_scaled", "Bearing"] )
        dictWriter.writeheader()
        dictWriter.writerows( compassValuesList )
