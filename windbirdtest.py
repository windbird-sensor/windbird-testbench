from serial import Serial
from time import sleep

def printRed(txt):
    print('\x1b[31m' + txt + '\x1b[39m')

class WindbirdTest():
    def __init__(self, port, baud=9600, timeout=3):
        self.ser = Serial(port)
        self.ser.baudrate = baud
        self.ser.timeout = timeout
        
    def __read(self):
        res = self.ser.readline()
        if len(res) == 0:
            raise Exception('Windbird is not responding')
        return res
    
    def __flush(self):
        self.ser.reset_output_buffer()
        self.ser.reset_input_buffer()
        self.ser.write(b'\03\r\n') # ctrl + c
        self.ser.read_until(b'\r\r\n')

    def __quit(self):
        for x in range(20):
            self.ser.write(b'q')
            sleep(1/100)
        self.ser.write(b'\03\r\n')

    def Hello(self):
        self.__flush()
        self.ser.write(b'\03\r\n') # ctrl + c
        if self.__read() != b'^C catched!\n':
            raise Exception('Windbird doesn\'t answer Hello')
        self.__read()
        self.__read()
            
    def ReadAdc(self, command):
        self.__flush()
        self.ser.write(b'adc ' + str.encode(command) + b'\r\n')
        self.__read()
        return int(self.__read()) / 1000
    
    def Led(self, setOn):
        self.__flush()
        if setOn:
            self.ser.write(b'led on\r\n')
        else:
            self.ser.write(b'led off\r\n')
        self.__read()
        if self.__read() != b'\x1b[32mok\x1b[m\r\n':
            printRed('LED command failed')
            
    def Gps(self, setOn):
        if setOn:
            self.__flush()
            self.ser.write(b'gps\r\n')
            self.__read()
            if self.__read() != b'Keep [q] pressed to stop\r\n':
                printRed('GPS ON command failed')
            self.__read()
        else:
            self.__quit()
            res = ''
            while True:
                res = self.__read()
                if res[:5] != b'GPGGA':
                    break
            if res != b'POWER OFF GPS...OK\r\n':
                printRed('GPS OFF command failed')
            return self.__read() == b'\x1b[32mok\x1b[m\r\n'
            
    def TestImu(self):
        self.__flush()
        self.ser.write(b'imu test\r\n')
        self.__read()
        self.__read()
        return self.__read() == b'\x1b[32mok\x1b[m\r\n'
        
    def SigfoxId(self):
        self.__flush()
        self.ser.write(b'sigfox id\r\n')
        self.__read()
        return self.__read().decode('utf-8').strip()
        
    def SigfoxCW(self, setOn):
         if setOn:
             self.__flush()
             self.ser.write(b'sigfox cw\r\n')
             self.__read()
             if self.__read() != b'Starting CW test at 868.13MHz\r\n':
                 printRed('SIGFOX CW ON command failed')
         else:
             self.ser.write(b'q')
             self.__read()
             self.__read()
             self.__read()
             return self.__read() == b'\x1b[32mok\x1b[m\r\n'
             
    def CountPulses(self):
        self.__flush()
        self.ser.write(b'speed test\r\n')
        self.__read()
        self.__read()
        return int(self.__read())
        
    def TestButton(self):
        self.__flush()
        self.ser.write(b'button\r\n')
        self.__read()
        self.__read()
        self.__read()
        while self.__read() == b'.\r\n':
            pass
        return True
