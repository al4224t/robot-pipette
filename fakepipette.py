import serial
from time import sleep

port = "\\\\.\\CNCA0"
ser = serial.Serial(port, 9600, timeout=0)

count = 0

while True:
	data = ser.read(9999)
	if len(data) > 0:
		print 'Got:', data
	
	if data == '/1Q':
		count = count+1
		if count == 4:
			ser.write('/0K')
		else:
			ser.write('/0`')

	sleep(0.5)
	#print 'not blocked'

ser.close()