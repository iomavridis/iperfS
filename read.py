import argparse
import serial
import threading
import time

# Instantiate the parser
parser = argparse.ArgumentParser(description='Serial Port communication. Creates data and sends them to the USB port \
                                             that Xbee device is connected')

parser.add_argument('--port', '-p', required=True, \
                    help='The serial port that it will be received the data')
args = parser.parse_args()

ser = serial.Serial(args.port)    # open serial port
while True:

	x = ser.read()
	print x
	if x == '?':
		break;

ser.close()