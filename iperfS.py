import argparse
import serial
import multiprocessing
import time

class ClientClass:
	"This is the Client Class for the iperf serial application"

	def __init__(self):
	 	self.baud = "9800"
	 	self.parity = "PARITY_NONE"
	 	self.stopB = "STOPBITS_ONE"
	 	self.timeout = 10 
	 	self.interval = 10
	 	self.bytesize = "EIGHTBITS"

	def parser(self, baud, parity, stopB, time, interval, bytesize):
		self.baud = baud
	 	self.parity = parity
	 	self.stopB = stopB
	 	self.timeout = time
	 	self.interval = interval
	 	self.bytesize = bytesize

	def open(self, port):
		ser = serial.Serial(
    		port='/dev/ttyUSB0',
    		baudrate=self.baud,
    		parity=getattr(serial,self.parity),
    		stopbits=getattr(serial,self.stopB),
    		bytesize=getattr(serial,self.bytesize)
		)
		return ser
	
	def setUpServer(self, ser, time, interval):
		while True:
			ser.write(b''+str(time)+' '+str(interval)+'\n')
	
	def sendData(self, ser):
		while True:
		 	ser.write(D)
	
	def listener(self, ser, thread):
		response = ser.readline().rstrip()
		exp_time = time.time() + 5
		if (response == "ok") or (time.time() > exp_time):
			thread.terminate()
			thread.join()
			print response

class ServerClass:
	"This is the Server Class for the iperf serial application"

##### Instantiate the parser #####
parser = argparse.ArgumentParser(description='Serial Port communication. Creates data and sends them to the USB port \
                                             that Xbee device is connected')
parser.add_argument('-H', metavar='host', dest='host', required=True, \
                    help='Server or Client')
parser.add_argument('-p', metavar='port', dest='port', required=True, \
					help='USB port of the device. e.g /dev/ttyUSB0')

# Create two argument groups
client_group = parser.add_argument_group(title='Client options')
serverClient_group = parser.add_argument_group(title='Server/Client options')

# Add arguments to those groups
client_group.add_argument('-t', metavar='time', dest='time', help='time in seconds to transmit for (default 10 secs)', \
							default=10)
client_group.add_argument('-i', metavar='interval', dest='interval', help='seconds between periodic bandwidth reports', \
							default=10)
serverClient_group.add_argument('--baudrate', metavar='baudrate', dest='baud', help='set baudrate (default 9600)', \
							 default=9600)
serverClient_group.add_argument('--parity', metavar='parity', dest='parity', help='parity bit (default PARITY_NONE)', default="PARITY_NONE")
serverClient_group.add_argument('--stopBit', metavar='stop bit', dest='stopB', help='Stop bit (default STOPBITS_ONE)', default="STOPBITS_ONE")
serverClient_group.add_argument('--bytesize', metavar='bytesize', dest='bytesize', help='Bytesize (default EIGHTBITS)', default="EIGHTBITS")
args = parser.parse_args()
##### Instantiate the parser #####

##### Server or Client #####
if args.host.lower() == 'client':
	client = ClientClass()
	
	#Parse arguments
	client.parser(args.baud, args.parity, args.stopB, args.time, args.interval, args.bytesize)

	#Open serial 
	ser = client.open(args.port)
	
	#Send timeout and interval time to Server 
	setUpThread = multiprocessing.Process(target = client.setUpServer, args = (ser, args.time, args.interval))
	setUpThread.start()

	#Listener
	client.listener(ser, setUpThread)

	#Send data
	#client.sendData(ser)

#else
	#....

##### Server or Client #####

