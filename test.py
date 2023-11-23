"""
import serial.tools.list_ports
import os

def get_connected_serial_devices():
    devices = serial.tools.list_ports.comports()
    return devices

while True:
    connected_serial_devices = get_connected_serial_devices()
    for device in connected_serial_devices:
        print(device.device)
    os.system('clear')
"""
import time
from adafruit_servokit import ServoKit

kit = ServoKit(channels=16)

# Specify the servo number connected to the PCA9685
servo_number = 0

# Set the servo angle (0 to 180 degrees)
kit.servo[servo_number].angle = 90
time.sleep(1)
kit.servo[servo_number].angle = 0
time.sleep(1)

# Cleanup
kit.servo[servo_number].angle = None