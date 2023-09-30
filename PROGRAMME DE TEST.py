from serial import Serial, serial_for_url
from time import sleep
import subprocess
import re
import os

import logging
import sys
import datetime

filename= 'test-'+datetime.datetime.now().strftime("%d-%m-%y_%H-%M")+'.log'

log = open(filename, 'w')

def print2(str):
    log.write(str+'\n')
    log.flush()
    print(str)

os.system('color')

from pydps5005 import DPS5005
from arduinotest import ArduinoTest
from windbirdtest import WindbirdTest

def printRed(txt):
    print2('\x1b[31m' + txt + '\x1b[39m')
def printGreen(txt):
    print2('\x1b[32m' + txt + '\x1b[39m')

def fail(txt):
    printRed(txt)
    raise Exception("Test aborted")

def test(txt, result, isFatal=False):
    if result:
        print2(txt + '\t\x1b[32m[OK]\x1b[39m')
    else:
        print2(txt + '\t\x1b[31m[FAIL]\x1b[39m')
        if isFatal:
            raise Exception("Test aborted")

def testValue(txt, value, min, max, isFatal=False):
    result = value >= min and value <= max
    txt = txt + ' [' + str(min) + '-' + str(max) + '] :\t' + str(value)
    test(txt, result, isFatal=isFatal)

def getPort(name, pid):
    try:
        port = serial_for_url('hwgrep://' + pid, do_not_open=True).port
        print2(name + ' on port ' + port)
        return port
    except:
        fail('ERROR: ' + name + ' not detected, check USB connection')

# PID:VID for WindBird connected through FTDI TTL232R-3V3
port_wb = getPort('WINDBIRD', '0403:6001')

# PID:VID for ARDUINO UNO R3
port_arduino = getPort('ARDUINO', '2341:0043')

# PID:VID for DPS5005 power supply
port_psu = getPort('POWER SUPPLY', '1A86:7523')


psu = DPS5005(port_psu)
ino = ArduinoTest(port_arduino)
wb = WindbirdTest(port_wb)

psu.DisableOutput()
psu.SetCurrent(0.1)
psu.SetVoltage(3.6)

#ino.Hello()

while True:
    print2('')
    input('**READY FOR TESTING. PRESS [ENTER] KEY TO START**')
    print2('---- START TESTING ----')

    try:
        psu.EnableOutput()
        sleep(1)

        testValue(
            'V_bench',
            psu.MeasVoltage(),
            3.56,
            3.64,
            isFatal=True)

        testValue(
            'V_batprot',
            ino.MeasVbatProtected(),
            3.5,
            3.7,
            isFatal=True)

        testValue(
            'V_main',
            ino.MeasVmain(),
            2.40,
            2.60,
            isFatal=True)

        testValue(
           'I_start',
           psu.MeasCurrent(),
           0,
           0.05,
           isFatal=True)

        print2('Flashing...')
	# flash = subprocess.run(['JLinkExe', 'flash_test.jlink'], # linux
        flash = subprocess.run(['c:\Program Files\SEGGER\JLink\JLink.exe', 'flash_test.jlink'], # windows
                               #stdout=subprocess.DEVNULL,
                               #stderr=subprocess.DEVNULL
                               capture_output=True
                               )
        flash_output = [s for s in flash.stdout.splitlines() if s]
        print2(flash_output[-4].decode('utf-8'))
        test('Flash firmware', flash_output[-3] == b'O.K.', isFatal=True)

        sleep(1)

        #wb.Hello()

        print2('ID\t0x' + wb.SigfoxId())
        print2('T°C\t' + str(wb.ReadAdc('tcpu') * 100))

        testValue(
            'V_aux',
            ino.MeasVaux(),
            2.40,
            2.60,
            isFatal=False)

        testValue(
            'ADC V_main',
            wb.ReadAdc('vcpu'),
            2.40,
            2.60,
            isFatal=False)

        testValue(
            'ADC V_bat',
            wb.ReadAdc('vbat'),
            3.5,
            3.7,
            isFatal=False)

        testValue(
            'ADC V_cap',
            wb.ReadAdc('vcap'),
            3.5,
            3.7,
            isFatal=False)


        wb.Led(1)
        sleep(1/10)
        testValue(
           'I_led',
           psu.MeasCurrent(),
           0.015,
           0.030,
           isFatal=False)
        testValue(
            'V_led',
            ino.MeasVled(),
            1.4,
            1.8,
            isFatal=False)
        wb.Led(0)

        test('IMU', wb.TestImu())

        ino.SendPulses()
        pulses = wb.CountPulses()
        test('Pulses [10] : ' + str(pulses), pulses == 10)


        wb.SigfoxCW(1)
        sleep(1)
        testValue(
           'I_radio',
           psu.MeasCurrent(),
           0.028,
           0.040,
           isFatal=False)
        wb.SigfoxCW(0)

        wb.Gps(1)
        sleep(1)
        testValue(
           'I_gps',
           psu.MeasCurrent(),
           0.012,
           0.025,
           isFatal=False)
        test('GPS', wb.Gps(0))

        sleep(0.5)
        testValue(
           'I_standby',
           psu.MeasCurrent(),
           0,
           0.002)

        print2('**PRESS THE BUTTON**')
        test('Button ', wb.TestButton())

    except Exception as e:
        printRed(str(e))
        printRed('Error during the test. Try again')

    psu.DisableOutput()

    print2('---- FINISHED TESTING ----')
#sleep(3)

#testValue(
#    'Courant au repos',
#    psu.MeasCurrent(),
#    0,
#    0.002,
#    isFatal=True)
# 
# print2('vbat\t' + str(arduino.MeasVbat()))
# print2('vbatp\t' + str(arduino.MeasVbatProtected()))
# print2('vcap\t' + str(arduino.MeasVcap()))
# print2('vmain\t' + str(arduino.MeasVmain()))
# print2('vaux\t' + str(arduino.MeasVaux()))
# print2('vled\t' + str(arduino.MeasVled()))