from serial import Serial

class ArduinoTest():
    def __init__(self, port, baud=9600, timeout=3):
        self.ser = Serial(port)
        self.ser.baudrate = baud
        self.ser.timeout = timeout
        
    def Hello(self):
        self.ser.reset_input_buffer()
        self.ser.write(b'h')
        if self.__read() != b'hello\r\n':
            raise Exception('Arduino doesn\'t answer Hello')
            
    def __read(self):
        res = self.ser.readline()
        if len(res) == 0:
            raise Exception('Arduino is not responding')
        return res
    
    def __meas(self, command):
        self.ser.flush()
        self.ser.write(command)
        return float(self.__read())

    def MeasVbat(self):
        return self.__meas(b'b')
        
    def MeasVbatProtected(self):
        return self.__meas(b'p')

    def MeasVcap(self):
        return self.__meas(b'c')

    def MeasVmain(self):
        return self.__meas(b'm')

    def MeasVaux(self):
        return self.__meas(b'x')

    def MeasVled(self):
        return self.__meas(b'l')

    def SendPulses(self):
        self.ser.write(b's')