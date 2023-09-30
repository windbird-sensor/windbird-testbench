#!/usr/bin/env python3

# from https://gist.github.com/four0four/c5421f49cdbf9ed9a1c659e0fe2b311e

from serial import Serial
from crcmod.predefined import mkPredefinedCrcFun

class PowerSupply():
    def __init__(self):
        self.v_set = 0.0
        self.i_set = 0.0

    """
        retrieves live measurement of current
    """
    def MeasCurrent():
        pass

    """
        retrieves live measurement of voltage
    """
    def MeasVoltage():
        pass

    """
        Sets current limit
    """
    def SetCurrent(self, current):
        self.i_set = current

    """
        Sets voltage limit
    """
    def SetVoltage(self, voltage):
        self.v_set = voltage

    """
        Gets current limit
    """
    def GetCurrent(self):
        return self.i_set

    """
        Gets voltage limit
    """
    def GetVoltage(self):
        return self.v_set

    def GetVersion(self):
        return "DUMMY"

    def GetModel(self):
        return "DUMMY"

class DPS5005(PowerSupply):

    CMD_READ= b'\x03'
    CMD_WRITE_SINGLE = b'\x06'
    MODBUS_ADDR = b'\x01'

    def __init__(self, ser, baud=9600, timeout=3):
        if type(ser) == type(Serial()):
            self.ser = ser
            self.ser.timeout = timeout
            if not ser.is_open:
                ser.open()
        else:
            self.device = ser
            self.ser = Serial(ser)
            self.ser.baudrate = baud

        self.__crc = mkPredefinedCrcFun("modbus")

    def EnableOutput(self):
        if self.__read_register(0x09) == '\x00\x01':
            return
        self.__write_register(0x09, 1)

    def DisableOutput(self):
        if self.__read_register(0x09) == '\x00\x00':
            return
        self.__write_register(0x09, 0)

    def MeasCurrent(self):
        return self.__read_register(0x03)/1000

    def MeasVoltage(self):
        return self.__read_register(0x02)/100

    def SetCurrent(self, current):
        self.i_set = int(current * 1000)
        self.__write_register(0x01, self.i_set)

    def SetVoltage(self, voltage):
        self.v_set = int(voltage * 100)
        self.__write_register(0x00, self.v_set)

    def GetVersion(self):
        return self.__read_register(0x0c)

    def GetModel(self):
        return self.__read_register(0x0b)

    def GetInputVoltage(self):
        return self.__read_register(0x05)/100

    def __read_register(self, reg):
        # [addr 1][0x03][reg start][n regs][crc]
        assert(reg < 0x10000)
        assert(reg > -1)
        pkt = self.MODBUS_ADDR + self.CMD_READ + reg.to_bytes(2, byteorder='big') + b'\x00\x01'
        # has to be sequential so eh..fuck it...
        pkt += self.__crc(pkt).to_bytes(2, byteorder='little') # yup
        self.ser.write(pkt)
        return int.from_bytes(self.__get_resp(), 'big')

    def __write_register(self, reg, val):
        # [addr 1][0x06][reg addr][reg data][crc]
        assert(reg < 0x10000)
        assert(reg > -1)
        pkt = self.MODBUS_ADDR + self.CMD_WRITE_SINGLE + reg.to_bytes(2, byteorder='big') + \
                val.to_bytes(2, byteorder='big')
        pkt += self.__crc(pkt).to_bytes(2, byteorder='little') # yup
        self.ser.write(pkt)
        self.__get_resp()

    def __get_resp(self):
        # TODO refactor
        addr = self.ser.read(1)
        func = self.ser.read(1)
        if func == self.CMD_WRITE_SINGLE:
            reg_addr = self.ser.read(2)
            reg_val = self.ser.read(2)
            crc = int.from_bytes(self.ser.read(2), 'little')
            assert(crc == self.__crc(addr+func+reg_addr+reg_val))
            return
        elif func == self.CMD_READ:
            nbytes = self.ser.read(1)
            data = self.ser.read(int.from_bytes(nbytes, 'big'))
            crc = int.from_bytes(self.ser.read(2), 'little')
            #print((addr+func+nbytes+data).hex())
            assert(crc == self.__crc(addr+func+nbytes+data))
            return data



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("uart", help="TTY/UART")
    parser.add_argument("--enable", action="store_true")
    parser.add_argument("--disable", action="store_true")
    args = parser.parse_args()

    t = DPS5005(args.uart)
    print("Model: %d, version %d"%(t.GetModel(), t.GetVersion()))
    print("Input voltage: %.2f"%(t.GetInputVoltage()))


    if args.enable:
        t.EnableOutput()
    elif args.disable:
        t.DisableOutput()
