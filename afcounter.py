import RPi.GPIO as GPIO
# initialize GPIO
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.cleanup()
from lib import tm1637
from datetime import datetime

current_date = datetime.now()
start_date = datetime(2023, 12, 31)

display = tm1637.TM1637(CLK=3, DIO=2, brightness=1.0)
display.ShowInt((current_date - start_date).days-1)
