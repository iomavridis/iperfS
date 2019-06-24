import argparse
import serial
import threading
import logging
import time
import os
import sys
import sched
from datetime import datetime, timedelta

class ClientClass:
	"This is the Client Class for the iperf serial application"

	def __init__(self):
		self.baud = "9800"
		self.parity = "PARITY_NONE"
		self.stopB = "STOPBITS_ONE"
		self.timeout = 10 
		self.interval = 10
		self.bytesize = "EIGHTBITS"

	def open(self, port, baud, parity, stopB, bytesize):
		#check if port is obtained correctly
		x = os.system("ls "+ port)
		if x != 0:
			sys.exit("Wrong port argument." + port + " does not exist!")

		ser = serial.Serial(
			port=port,
			baudrate=baud,
			parity=getattr(serial,parity),
			stopbits=getattr(serial,stopB),
			bytesize=getattr(serial,bytesize)
		)
		return ser
	
	def setUpServer(self, ser, time, interval):
		ser.write(b''+str(time)+' '+str(interval)+'\n')

	def sendData(self, ser):
		global dead
		global send
		count = 0
		while ( not send):
			pass
		#print "Start send", datetime.now()
		while ( not dead ):
			ser.write('D')
			count += 1
		#print "Stop send", datetime.now()
		#"The packets that client has send to the server:", count
	
	def listener(self, ser):
		global dead
		global send
		while ( not dead ):
			response = ser.readline()
			if ("send" in response):
				send = True
			if ("Total" in response):
				dead = True
				print response
			if ("Report" in response):
				print response
	

class ServerClass:
	"This is the Server Class for the iperf serial application"

	def __init__(self):
		self.baud = "9800"
		self.parity = "PARITY_NONE"
		self.stopB = "STOPBITS_ONE"
		self.timeout = 10 
		self.interval = 10
		self.bytesize = "EIGHTBITS"
		self.data = list()

	def open(self, port, baud, parity, stopB, bytesize):
		#check if port is obtained correctly
		x = os.system("ls "+ port)
		if x != 0:
			sys.exit("Wrong port argument." + port + " does not exist!")

		ser = serial.Serial(
			port=port,
			baudrate=baud,
			parity=getattr(serial,parity),
			stopbits=getattr(serial,stopB),
			bytesize=getattr(serial,bytesize)
		)
		return ser
	
	def bandwidth(self, ser, durationTime, rep, tag):
		global previousData
		curentData = len(self.data)
		bandwidth = (curentData - previousData)* 10 / (float(durationTime) * 1000 )
		previousData = curentData
		start = rep * int(durationTime)
		stop = (rep + 1) * int(durationTime) 
		message = str(tag)+" " + str(start) + "-" + str(stop) +  "  Bandwidth: " + str(round(bandwidth,2)) + " Kbps"
		print message
		ser.write(b''+ str(message) + '\n')

	def totalReport(self, ser):
		curentData = len(self.data)
		bandwidth = curentData * 10 / (float(self.timeout) * 1000 )
		start = 0
		stop = self.timeout 
		message = "Total " + str(start) + "-" + str(stop) +  "  Bandwidth: " + str(round(bandwidth,2)) + " Kbps"
		print message
		ser.write(b'' + str(message) + '\n')


	def periodicReports(self, ser, startTime, stopTime, reps):
		print "Print startTime inside periodicReports function: ", startTime
		for i in range(1, reps + 1):
			run_at =  startTime + timedelta( seconds= i * int(self.interval))
			delay = (run_at - startTime).total_seconds()
			threading.Timer(delay, self.bandwidth).start()
			#s.scheduler(time)
			#s.run(bandwidth())

	def setupListener(self, ser):
		response = ser.readline().split()
		timeout = response[0]
		interval = response[1]
		return timeout, interval

	def dataListener(self, ser, startTime, stopTime):
		while (time.time() < startTime):
			pass
		#Tell the client to start sending 
		ser.write(b'send\n') 
		#print "Start listen", datetime.now()
		while time.time() < stopTime:
			char = ser.read()
			self.data.append(char)
		#print "Stop listen", datetime.now()

		
if __name__ == "__main__":
	global dead, send, previousData
	dead = False
	send = False
	previousData = 0
	format = "%(asctime)s: %(message)s"
	#logging.basicConfig(format=format, level=logging.INFO,
	#					datefmt="%H:%M:%S")
	logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S', level=logging.INFO)

	##### Instantiate the parser #####
	parser = argparse.ArgumentParser(description='Serial Port communication. Creates data and sends them to the USB port \
												 that Xbee device is connected')
	parser.add_argument('-S', '--server', dest='server', help="Server mode", action="store_true")
	parser.add_argument('-C', '--client', dest='client', help="Client mode", action="store_true")
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
	if args.client :
		client = ClientClass()
		
		#Parse arguments
		client.baud = args.baud
		client.parity = args.parity
		client.stopB = args.stopB
		client.timeout = args.time
		client.interval = args.interval
		client.bytesize = args.bytesize
		#Open serial 
		ser = client.open(args.port, client.baud, client.parity, client.stopB, client.bytesize)
		
		#Send timeout and interval time to Server 
		client.setUpServer(ser, args.time, args.interval)

		#Send data
		sendData = threading.Thread(target=client.sendData, args=(ser,))
		listener = threading.Thread(target=client.listener, args=(ser, ))
		sendData.start()
		listener.start()

		sendData.join()
		ser.close()
		#Listener
	#	client.listener(ser)

	else:

		server = ServerClass()

		#Parse arguments
		server.baud = args.baud
		server.parity = args.parity
		server.stopB = args.stopB
		server.bytesize = args.bytesize

		#Open serial 
		ser = server.open(args.port, server.baud, server.parity, server.stopB, server.bytesize)
	 
		#SetupListener (Get timeout and interval time from client)
		timeout, interval = server.setupListener(ser)
		server.timeout = filter(lambda x: x.isdigit(), timeout)
		server.interval = filter(lambda x: x.isdigit(), interval)
		
		#Define start/stop time and periodic reports
		startTime = time.time() + 2
		stopTime = startTime + int(server.timeout)
		reps = int(server.timeout) / int(server.interval)

		dataListener = threading.Thread(target=server.dataListener, args=(ser, startTime, stopTime))
		dataListener.start()

		# Set up scheduler
		s = sched.scheduler(time.time, time.sleep)
		for i in range(0, reps):
			timeToRun = startTime +  (i+1) * int(interval)
			s.enterabs(timeToRun, 1, server.bandwidth, argument=(ser, server.interval, i,"Report"))
			#reportsTime.append(time)
		s.run()

		periodicReports = threading.Thread(target=server.periodicReports, args=(ser, startTime, stopTime, reps))


		dataListener.join()
		server.totalReport(ser)

		ser.close()

	##### Server or Client #####


