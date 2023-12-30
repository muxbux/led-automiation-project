import RPi.GPIO as GPIO
import time


ledblue = 19				# PWM pin connected to LED
ledred = 13				# PWM pin connected to LED
ledgreen = 12
# GPIO-instellingen
GPIO.setmode(GPIO.BCM)
GPIO.setup(ledblue, GPIO.OUT)
GPIO.setup(ledred, GPIO.OUT)
GPIO.setup(ledgreen, GPIO.OUT)

# Zet de blauwe LED aan
GPIO.output(ledblue, GPIO.HIGH)
time.sleep(1)  # Wacht 1 seconde
GPIO.output(ledblue, GPIO.LOW)

# Zet de rode LED aan
GPIO.output(ledred, GPIO.HIGH)
time.sleep(1)
GPIO.output(ledred, GPIO.LOW)

# Zet de groene LED aan
GPIO.output(ledgreen, GPIO.HIGH)
time.sleep(1)
GPIO.output(ledgreen, GPIO.LOW)

# GPIO opruimen
GPIO.cleanup()
