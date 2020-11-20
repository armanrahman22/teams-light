#!/usr/bin/env python3
# pylint: disable=no-member
import time
from graph_api import get_presence

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(
        "Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script"
    )

RED = 9
YELLOW = 10
GREEN = 11
COLORS = [RED, YELLOW, GREEN]

GPIO.setmode(GPIO.BCM)  # Broadcom pin-numbering scheme
GPIO.setup(COLORS, GPIO.OUT)  # Red LED pin set as output


def turn_off_others(desired):
    for color in COLORS:
        if color != desired:
            GPIO.output(color, False)


# Initial state for LEDs:
print("Testing RF out, Press CTRL+C to exit")

try:
    while True:
        availability = get_presence()
        if availability == "Available":
            turn_off_others(GREEN)
            GPIO.output(GREEN, True)
        elif availability == "Busy":
            turn_off_others(RED)
            GPIO.output(RED, True)
        else:
            turn_off_others(YELLOW)
            GPIO.output(YELLOW, True)
        time.sleep(5)

except KeyboardInterrupt:  # If CTRL+C is pressed, exit cleanly:
    print("Keyboard interrupt")

except:
    print("some error")

finally:
    print("clean up")
    GPIO.cleanup()  # cleanup all GPIO
