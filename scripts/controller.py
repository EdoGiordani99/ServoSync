import time

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

