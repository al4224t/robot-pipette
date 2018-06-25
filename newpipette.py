import serial
import json
import os
import sys
import inspect
from time import sleep

HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(HERE_PATH)

ROBOT_CONFIG_FILE = os.path.join(HERE_PATH, 'newrobot_config.json')
PIPETTE_PROFILES_FILE = os.path.join(HERE_PATH, 'pipette_profiles.json')
PIPETTE_ERRORS_FILE = os.path.join(HERE_PATH, 'pipette_errors.json')

class Pipette(object):

	def __init__(self, port, incr_mode, increments, empty_level, total_volume):
		self.incr_mode = incr_mode
		self.empty_level = empty_level
		self.total_volume = total_volume
		self.current_volume = 0
		self.home_volume = -1000 # uL
		
		#load speed profiles from file "pipette_profiles.json"
		self.profiles = self.profiles_from_file()
		
		#open serial connection and initialize
		self.open_serial(port)
		self.send_initialize()
		self.set_increment(incr_mode, increments)
		self.speed_profile('default')
		
	## SETUP
	@classmethod
	def from_config(cls, config):
		port = config['devices']['P']['config']['port']
		incr_mode = config['devices']['P']['config']['incr_mode']
		empty_level = config['devices']['P']['config']['empty_volume']
		total_volume = config['devices']['P']['config']['total_volume']
		increments = config['devices']['P']['increments']
		return cls(port, incr_mode, increments, empty_level, total_volume)
		
	def profiles_from_file(self, file=PIPETTE_PROFILES_FILE):
		with open(file) as f:
			return json.load(f)
			
	def errors_from_file(self, file=PIPETTE_ERRORS_FILE):
		with open(file) as f:
			return json.load(f)
			
	def resolve_error_code(self, status):
		#load the error info from file "pipette_errors.json"
		self.errors = self.errors_from_file()
		self.error_number = (ord(status) & 0x1F)
		return self.errors['error_codes'][self.error_number]
		
	def open_serial(self, port):
		self.ser = serial.Serial(port,9600,timeout=1)
	
	def close_serial(self):
		self.ser.close()
	
	## COMMANDS
	def send_initialize(self):
		self.command = '/1ZR'
		self.ser.write(self.command)
		sleep(1)
		
	def send_command(self, data):
		self.wait_until_idle()
		self.command = '/1{}R'.format(data)
		self.ser.write(self.command)
		sleep(1)
		
	def send_query(self):
		self.command = '/1Q'
		self.ser.write(self.command)
		self.response = self.ser.read(3)
		print 'Got:', self.response
		return self.response[2]

	## CONFIGURATION
	def set_increment(self, incr_mode, increments):
		#if not default mode, send command to change mode
		if incr_mode != 'N0':
			self.send_command('{}'.format(incr_mode))
		self.ul_per_incr = increments[incr_mode]
		print self.ul_per_incr
		return 'Increment mode set to {}'.format(incr_mode)
		
	def start_velocity(self, ul_per_sec):
		self.incr_per_sec = str(int((ul_per_sec/self.ul_per_incr)+0.5))
		self.send_command('v{}'.format(self.incr_per_sec))

	def top_velocity(self, ul_per_sec):
		self.incr_per_sec = str(int((ul_per_sec/self.ul_per_incr)+0.5))
		self.send_command('V{}'.format(self.incr_per_sec))

	def cutoff_velocity(self, ul_per_sec):
		self.incr_per_sec = str(int((ul_per_sec/self.ul_per_incr)+0.5))
		self.send_command('c{}'.format(self.incr_per_sec))

	def acceleration_deceleration(self, slope_code_accel=14, slope_code_decel=14):
		self.send_command('L{},{}'.format(slope_code_accel,slope_code_decel))
		
	def speed_profile(self, substance):
		self.start_velocity(self.profiles[substance]['start_velocity'])
		self.top_velocity(self.profiles[substance]['top_velocity'])
		self.cutoff_velocity(self.profiles[substance]['cutoff_velocity'])
		self.acceleration_deceleration(self.profiles[substance]['acceleration'],self.profiles[substance]['deceleration'])
	
	## BASIC FUNCTIONS
	def qualified_move(self, target_volume, time_in_ms, pressure_th):
		self.target_position = str(int((target_volume / self.ul_per_incr)+0.5))
		self.send_command('p4q{},{}A{}'.format(time_in_ms, pressure_th, self.target_position))
		self.wait_until_idle()
		self.current_volume = target_volume
				
	def absolute_move(self, target_volume):
		self.target_position = str(int((target_volume / self.ul_per_incr)+0.5))
		self.send_command('A{}'.format(self.target_position))
		self.current_volume = target_volume

	def wait_until_idle(self):
		while True:
			self.status = self.send_query()
			if self.status == '`':
				print 'idle'
				break
			if self.status != '@':
				#if not idle or busy, must be an error. Throw an exception including the error information
				raise Exception('Pipette error {}'.format(self.resolve_error_code(self.status)))
			#pipette busy, so wait a little then check again
			sleep(1)
		
	def aspirate(self, volume_to_aspirate, time_in_ms = 0, pressure_th = 0):
		if (volume_to_aspirate <= (self.total_volume - self.current_volume)):
			if time_in_ms == 0:
				self.absolute_move(volume_to_aspirate + self.current_volume)
			else:
				self.qualified_move(volume_to_aspirate + self.current_volume, time_in_ms, pressure_th)
			return 'Volume {}uL aspirated into pipette'.format(volume_to_aspirate)
		else:
			raise Exception('Not enough space in pipette to aspirate {}uL'.format(volume_to_aspirate))
			
	def dispense(self, volume_to_dispense, time_in_ms = 0, pressure_th = 0):
		if (volume_to_dispense <= (self.current_volume - self.empty_level)):
			if time_in_ms == 0:
				self.absolute_move(self.current_volume - volume_to_dispense)
			else:
				self.qualified_move(self.current_volume - volume_to_dispense, time_in_ms, pressure_th)
			return 'Volume {}uL dispensed from pipette'.format(volume_to_dispense)
		else:
			raise Exception('Not enough in pipette to dispense {}uL'.format(volume_to_dispense))
			
	## TESTING
	@classmethod
	def from_configfile(cls, configfile=ROBOT_CONFIG_FILE):
		with open(configfile) as f:
			return cls.from_config(json.load(f))
			

p = Pipette.from_configfile()
#test = 'k'
#test = ord(test)
#print test
#test = (test & 0x20)
#test = (test >> 5)
#print test
p.aspirate(700, 5000, 20)
p.dispense(500, 3000, 20)
p.aspirate(800)
p.aspirate(1)
p.close_serial()