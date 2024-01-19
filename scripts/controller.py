import time
import requests
import threading
import os

from pyfirmata import Arduino


class Servo:
    def __init__(self, pin, board) -> None:
        self.pin = pin
        self.servo = board.get_pin('d:{}:s'.format(self.pin))
        self.name = f"Servo_{pin}"
    
    def set_angle(self, angle):
        self.servo.write(angle)


class Controller:
    def __init__(self, max_retry_number:int=3) -> None:
        
        self.max_retry_number = max_retry_number

        # Connecting Arduinio
        self.connect_to_arduino()
        
        # Connecting Servos
        self.servos_init()

    def servos_init(self):
        self.servos = [None for i in range(8)]
        self.available_pins = list(range(8, 14))

        if self.connected:
            for i in self.available_pins:
                self.servos.append(Servo(i, self.board))

    def connect_to_arduino(self):
        print("Conntecting to Arduino Board:")
        for i in range(self.max_retry_number):
            try:
                self.port = "/dev/cu.usbmodem14101" 
                self.board = Arduino(self.port)
                self.connected = True
                print(f"Trial {i+1} Succeded!")
                break
            except: 
                self.connected = False
                self.port, self.board = None, None
                print(f"Trial {i+1} Failed")
            time.sleep(1)

    def move(self, servo_pin, angle):
        self.servos[servo_pin].set_angle(angle)

    def get_servos_names(self):
        return [s.name for s in self.servos if s is not None]
    
class WiFiServo:
    def __init__(self, pin) -> None:
        self.pin = pin
        self.name = f"Servo_{pin}"

class WiFiController:
    def __init__(self, max_retry_number:int=3) -> None:
        
        self.max_retry_number = max_retry_number
        self.servos = []

        self.ESP32_IP = "192.168.1.202"

        self.servos_init()
        self.connected = self.check_connection()
    
    def servos_init (self):
        for i in range(16):
            self.servos.append(WiFiServo(i))

    def connect_to_arduino(self):
        pass


    def check_connection(self, max_retry_number:int=3, max_seconds:int=5):

        for i in range(max_retry_number):
            print(f"Trial {i+1} ...")
            try: 
                url = f"http://{self.ESP32_IP}/connectionCheck"
                response = requests.get(url, timeout=max_seconds)
                print("Connected")
                return True
            except requests.exceptions.RequestException as e:
                print("Failed")
        return False

    def move_servo(self, servo_pin, angle):
        
        try: 
            url = f"http://{self.ESP32_IP}/setAngle?servo_num={servo_pin}&angle={angle}"
            response = requests.get(url, timeout=1)
            os.system("clear")
            print("GOOD CONNECTION")

        except requests.exceptions.RequestException as e:
            os.system("clear")
            print("BAD CONNECTION")
    
    def move(self, servo_pin, angle):
        threading.Thread(target=self.move_servo, args=(servo_pin, angle)).start()

    def get_servos_names(self):
        return [s.name for s in self.servos if s is not None]

