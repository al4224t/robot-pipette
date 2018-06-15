import serial
import json
import os
import sys
import inspect
from time import sleep

HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(HERE_PATH)

ROBOT_CONFIG_FILE = os.path.join(HERE_PATH, 'newrobot_config.json')

class Pipette(object):

	def __init__(self, port, incr_mode, increments, empty_level, total_volume):
		self.incr_mode = incr_mode
		self.empty_level = empty_level
		self.total_volume = total_volume
		self.current_volume = 0
		self.home_volume = -1000 # uL
		self.open_serial(port)
		self.initialize()
		self.set_increment(incr_mode, incr_lookup)
		
	## CONFIG
	@classmethod
	def from_config(cls, config):
		port = config['devices']['P']['config']['port']
		incr_mode = config['devices']['P']['config']['incr_mode']
		empty_level = config['devices']['P']['config']['empty_volume']
		total_volume = config['devices']['P']['config']['total_volume']
		increments = config['devices']['P']['increments']
		return cls(port, incr_mode, increments, empty_level, total_volume)
		
	## SERIAL CONNECTION TO PIPETTE
	def open_serial(self, port):
		self.ser = serial.Serial(port,9600,timeout=1)
	
	def close_serial(self):
		self.ser.close()
	
	## COMMANDS
	def initialize(self):
		self.command = '/1ZR'
		self.ser.write(self.command)
		sleep(1)
		
	def set_increment(self, incr_mode, increments):
		#if not default mode, send command to change mode
		if incr_mode != 'N0':
			self.command = '/1{}R'.format(incr_mode)
			self.ser.write(self.command)
			sleep(1)
		self.ul_per_incr = increments[{}].format(incr_mode)
		print self.ul_per_incr
		return 'Increment mode set to {}'.format(incr_mode)
		
	def absolute_move(self, target_volume):
		self.target_position = str(int((target_volume/self.ul_per_incr)+0.5))
		self.wait_until_idle()
		self.command = '/1A{}R'.format(self.target_position)
		self.ser.write(self.command)
		sleep(1)
		self.current_volume = target_volume
		
	def query(self):
		self.command= '/1Q'
		self.ser.write(self.command)
		self.response = self.ser.read(3)
		print 'Got:', self.response
		return self.response[2]
	
	## FUNCTIONS
	def wait_until_idle(self):
		while True:
			self.status = self.query()
			if self.status == '`':
				print 'ready'
				break
			wait(1)
		
	def aspirate(self, volume_to_aspirate):
		if (volume_to_aspirate <= (self.total_volume - self.current_volume)):
			self.absolute_move(volume_to_aspirate+self.current_volume)
			return 'Volume {}uL aspirated into pipette'.format(volume_to_aspirate)
		else:
			raise Exception('Not enough space in pipette to aspirate {}uL'.format(volume_to_aspirate))
			
	def dispense(self, volume_to_dispense):
		if (volume_to_dispense <= (self.current_volume - self.empty_level)):
			self.absolute_move(self.current_volume-volume_to_dispense)
			return 'Volume {}uL dispensed from pipette'.format(volume_to_dispense)
		else:
			raise Exception('Not enough in pipette to dispense {}uL'.format(volume_to_dispense))
			
	## TESTING
	@classmethod
	def from_configfile(cls, configfile=ROBOT_CONFIG_FILE):
		with open(configfile) as f:
			return cls.from_config(json.load(f))
			

p = Pipette.from_configfile()
p.aspirate(700)
p.dispense(500)
p.aspirate(800)
p.dispense(1001)
p.close_serial()