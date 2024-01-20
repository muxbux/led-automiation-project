# SPDX-FileCopyrightText: 2017 Tony DiCola for Adafruit Industries
# SPDX-FileCopyrightText: 2017 James DeVito for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example is for use on (Linux) computers that are using CPython with
# Adafruit Blinka to support CircuitPython libraries. CircuitPython does
# not support PIL/pillow (python imaging library)!

from time import sleep
import subprocess

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

import threading

import off_settings
import clock_colors
import main_settings
import mqtt_manager as mqttmanager
import network

from datetime import datetime, time, timedelta

import colorsys
#import datetime

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
disp = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

# Clear display.
disp.fill(0)
disp.show()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new("1", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0


# Load default font.
font = ImageFont.load_default()

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 9)

reading = "Not Active"
reader = SimpleMFRC522()

ledblue = 19				# PWM pin connected to LED
ledred = 13				# PWM pin connected to LED
ledgreen = 12				# PWM pin connected to LED
buttonpin = 26

GPIO.setwarnings(False)			#disable warnings

GPIO.setup(ledblue,GPIO.OUT)
blue = GPIO.PWM(ledblue,1000)		#create PWM instance with frequency
blue.start(0)				#start PWM of required Duty Cycle 


GPIO.setup(ledred,GPIO.OUT)
red = GPIO.PWM(ledred,1000)		#create PWM instance with frequency
red.start(0)				#start PWM of required Duty Cycle 


GPIO.setup(ledgreen,GPIO.OUT)
green = GPIO.PWM(ledgreen,1000)		#create PWM instance with frequency
green.start(0)				#start PWM of required Duty Cycle 

GPIO.setup(buttonpin, GPIO.IN, pull_up_down=GPIO.PUD_UP)


lan = False
darkmode = False

brightnesscontrol = 0
dir = 0.1
huecolor = 0

counter = 0


def hue_to_rgb(hue):
    # Ensure that hue is in the range [0, 1]
    hue = hue / 360
    hue = hue % 1.0

    # Convert hue to RGB using colorsys
    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)

    # Scale RGB values to the range [0, 100]
    r = int(r * 100)
    g = int(g * 100)
    b = int(b * 100)

    return r, g, b



while True:
    last_main_settings = main_settings.get_last_off_settings()
    last_clock_colors = clock_colors.get_last_off_settings()
    last_off_settings = off_settings.get_last_off_settings()


    datastring = (
        str(int(last_main_settings.hue)) + ";" +
        str(last_main_settings.mode) + ";" +
        str(int(last_clock_colors.hue_hour)) + ";" +
        str(int(last_clock_colors.hue_minutes)) + ";" +
        str(int(last_clock_colors.hue_seconds)) + ";" +
        str(darkmode)
    )


    mqttmanager.send_data(datastring)

    

    for i in range (1000):
        # Check if the button is pressed and adjust the mode
        if GPIO.input(buttonpin) == GPIO.LOW:
            last_main_settings.mode += 1
            if last_main_settings.mode == 4:
                last_main_settings.mode = 0
            main_settings.write_to_main_settings(last_main_settings)
            last_main_settings = main_settings.get_last_off_settings()
        while GPIO.input(buttonpin) == GPIO.LOW:
            sleep(0.1)
        
        #ledstripcontrol
        if(darkmode == False):
            if last_main_settings.mode == 0:
                red.ChangeDutyCycle(0)
                blue.ChangeDutyCycle(0)
                green.ChangeDutyCycle(0)


            elif last_main_settings.mode == 1:
                red.ChangeDutyCycle(last_main_settings.r_value/2.55)
                blue.ChangeDutyCycle(last_main_settings.b_value/2.55)
                green.ChangeDutyCycle(last_main_settings.g_value/2.55)


            elif last_main_settings.mode == 2:

                if(brightnesscontrol >= 99):
                    dir = -0.05
                if(brightnesscontrol <= 1):
                    dir = 0.05

                brightnesscontrol = brightnesscontrol + dir
                # print(brightnesscontrol)
                red.ChangeDutyCycle((last_main_settings.r_value/2.55) * brightnesscontrol/100)
                blue.ChangeDutyCycle((last_main_settings.b_value/2.55) * brightnesscontrol/100)
                green.ChangeDutyCycle((last_main_settings.g_value/2.55)* brightnesscontrol/100)


            elif last_main_settings.mode == 3:
                if(huecolor >= 359):
                    dir = -0.05
                if(huecolor <= 0.06):
                    dir = 0.05

                huecolor = huecolor + dir
                r,g,b = hue_to_rgb(huecolor)
                red.ChangeDutyCycle((r /2.55))
                blue.ChangeDutyCycle((g /2.55))
                green.ChangeDutyCycle((b /2.55))
        else:
            red.ChangeDutyCycle(0)
            blue.ChangeDutyCycle(0)
            green.ChangeDutyCycle(0)
        sleep(1/1000)

    last_off_settings_with_time = off_settings.get_last_off_settings_with_dark_mode()

    formatted_time = datetime.now().time()
    formatted_time_parts = formatted_time.strftime("%H:%M").split(":")
    formatted_time = time(int(formatted_time_parts[0]), int(formatted_time_parts[1]))

    # Convert darkModeStartTime and darkModeEndTime to datetime.time if they are timedelta
    if isinstance(last_off_settings_with_time.darkModeStartTime, timedelta):
        last_off_settings_with_time.darkModeStartTime = (datetime.min + last_off_settings_with_time.darkModeStartTime).time()

    if isinstance(last_off_settings_with_time.darkModeEndTime, timedelta):
        last_off_settings_with_time.darkModeEndTime = (datetime.min + last_off_settings_with_time.darkModeEndTime).time()

    # Ensure darkModeEndTime is after darkModeStartTime
    if last_off_settings_with_time.darkModeEndTime < last_off_settings_with_time.darkModeStartTime:
        # Swap the values if necessary
        last_off_settings_with_time.darkModeStartTime, last_off_settings_with_time.darkModeEndTime = (
            last_off_settings_with_time.darkModeEndTime,
            last_off_settings_with_time.darkModeStartTime,
        )

    # Check if formatted_time is between darkModeStartTime and darkModeEndTime
    is_between_times = (
        last_off_settings_with_time.darkModeStartTime <= formatted_time <= last_off_settings_with_time.darkModeEndTime
    )

    # print("starttime: " + str(last_off_settings_with_time.darkModeStartTime))
    # print("endtime: " + str(last_off_settings_with_time.darkModeEndTime))
    # print("formattime: " + str(formatted_time))
    # print("is between times: " + str(is_between_times))
    # print("\n")

    lan = network.is_ip_active("192.168.0.120")
    if(is_between_times):
        darkmode = True
    if(last_off_settings.enableDarkMode):
        darkmode = True
    if((last_off_settings.prioritizeRFID == True and reading == "Activated") or (last_off_settings.prioritizeLAN == True and lan  == False)):
        darkmode = False
        
    # print("lan on?: " + str(lan))
    # print("prio rfid: " + str(last_off_settings.prioritizeRFID))
    # print("prio lan: " + str(last_off_settings.prioritizeLAN))
    # print("isbetweentimes: " + str(is_between_times))
    # print("darkmode: " + str(darkmode))



    #oled control
    if(True):
        #draw text on oleddisplay
        draw.rectangle((0, 0, width, height), outline=0, fill=0)
        if id is not None:
            reader.read_no_block()
        id, text = reader.read_no_block()
        if id is not None:
            # print("ID: %s" % id)
            reading = "Activated"
        else:
            # print('None')
            reading = "Not Active"

        # Shell scripts for system monitoring from here:
        # https://unix.stackexchange.com/questions/119126/command-to-display-memory-usage-disk-usage-and-cpu-load
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        
        # Write four lines of text.

        draw.text((x, top + 0), "IP: " + IP, font = font, fill = 255)
        draw.text((x, top + 8), "Reading: " + reading, font = font, fill =255)
        draw.text((x, top + 16), "Mode: " + str(last_main_settings.mode), font = font, fill =255)

        
        if(darkmode):
            oleddark = "on"
            if(last_off_settings.enableDarkMode): oleddark = "on"
            if(is_between_times): oleddark = "time"
        else:
            oleddark = "off"
            if(last_off_settings.prioritizeRFID == True and reading == "Activated"):oleddark = "rfid prio"
            if(last_off_settings.prioritizeLAN == True and lan  == False): oleddark = "lan prio"

        draw.text((x, top + 24), "darkmode: " + oleddark, font = font, fill =255)
        
        
        # Display image.
        disp.image(image)
        disp.show()
        sleep(0.0001)
