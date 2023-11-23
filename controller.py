from pyfirmata import Arduino, SERVO
import time


class Controller:

    def __init__(self, port:str='/dev/cu.usbmodem14201'):

        self.arduino_port = port
        self.board = Arduino(self.arduino_port)

        self.servos = {}
        self.servos_name = {}

    def set_port_value(self, port: str):
        self.arduino_port = port

    def add_servo(self, pin, servo_name):
        if pin not in self.servos:
            self.servos[pin] = self.board.get_pin('d:{}:s'.format(pin))
            self.servos_name[pin] = servo_name
            return True
        else:
            return False









# Define the port where your Arduino is connected (change this to your port)
arduino_port = '/dev/cu.usbmodem14201'

# Create a connection to the Arduino
board = Arduino(arduino_port)

# Define the pin to which the servo is connected
servo_pin = 12  # You can change this to the pin where you connect the servo

# Attach the servo to the specified pin
servo = board.get_pin('d:{}:s'.format(servo_pin))

try:
    while True:
        # Move the servo to the starting position
        servo.write(90)
        print("90")
        time.sleep(1)

        # Move the servo to the other position
        servo.write(180)
        print("180")
        time.sleep(1)

except KeyboardInterrupt:
    # Move the servo back to the starting position when the program is interrupted
    servo.write(90)

finally:
    # Close the connection to the Arduino
    board.exit()

