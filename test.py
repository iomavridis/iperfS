import time
import serial
parity = "PARITY_NONE"
baud = "9600"
# configure the serial connections (the parameters differs on the device you are connecting to)
ser = serial.Serial(
    port='/dev/ttyUSB1',
    baudrate=baud,
    parity=getattr(serial,parity),
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

ser.write(b'ok\n')

ser.close()