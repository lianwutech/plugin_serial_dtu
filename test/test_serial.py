#coding=utf-8

import time
import serial

def hexShow(argv):
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        result += hhex+' '
    print 'hexShow:',result

ser = serial.Serial( #下面这些参数根据情况修改
    port='/dev/tty.SLAB_USBtoUART',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

for i in range(0, 1):
    n = ser.write("\x01\x04\x00\x00\x00\x00\x01\x31\xCA")
    print n
    str = ser.read(n)
    hexShow(str)
