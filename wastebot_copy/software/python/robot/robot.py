"""
    coding: UTF-8
    Python 2.7

    robot.py

    Created 07/06/2016
    Kevin Donkers, The Cronin Group, University of Glasgow

    Robot control for Wastebot
"""
# system imports
import os
import sys
import inspect
import json

# add robot path to access files within same folder as robot.py
HERE_PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(HERE_PATH)

# project modules
from commanduino import CommandManager
from commanduino.devices.axis import Axis, MultiAxis
from pipette import Pipette
from shaker import Shaker
from two_dim_rack import TwoDimRack

# logging
import logging
logging.basicConfig(level=logging.INFO)

# link to default robot_config and arena_config files
ROBOT_CONFIG_FILE = os.path.join(HERE_PATH, 'robot_config.json')
ARENA_CONFIG_FILE = os.path.join(HERE_PATH, 'arena_config.json')

# default parameters
DEFAULT_XYZ_AXIS = {'mm_per_step': 0.00935,
                    'min': 0,
                    'max': 100}
DEFAULT_P_AXIS = {'ul_per_step': 0.01,
                    'min': 0,
                    'max': 100}
DEFAULT_S_AXIS = {'deg_per_step': 0.05625,
					'min': -1000,
					'max': 1000}

class Robot(object):

	def __init__(self, config, xaxis=DEFAULT_XYZ_AXIS, yaxis=DEFAULT_XYZ_AXIS, zaxis=DEFAULT_XYZ_AXIS, paxis=DEFAULT_P_AXIS, saxis=DEFAULT_S_AXIS):
		'''Initialize parts of robot'''
		self.cmdMng = CommandManager.from_config(config)
		#self.x = Axis(self.cmdMng.X, xaxis['mm_per_step'], xaxis['min'], xaxis['max'])
		#self.y = Axis(self.cmdMng.Y, yaxis['mm_per_step'], yaxis['min'], yaxis['max'])
		#self.z = Axis(self.cmdMng.Z, zaxis['mm_per_step'], zaxis['min'], zaxis['max'])
		#self.xy = MultiAxis(self.x, self.y)
		#self.xyz = MultiAxis(self.x, self.y, self.z)
		#self.p = Pipette(Axis(self.cmdMng.P, paxis['ul_per_step'], paxis['min'], paxis['max']), paxis['min'], paxis['max'])
		self.s = Shaker(self.cmdMng.S, saxis['deg_per_step'], saxis['min'], saxis['max'])
		'''Initialize arena'''
		self.arena = self.arena_from_configfile()
		self.tools = self.extract_dict_from_dict(self.arena, 'tools')
		self.wellplates = self.extract_rack_from_dict(self.arena, 'wellplates')
		if 'tipracks' in self.arena:
			self.tipracks = self.extract_rack_from_dict(self.arena, 'tipracks')
		'''Tracking parameters'''
		self.liquid_height = 0
		'''Home robot axes'''
		#self.home()

		
	## CONFIG
	@classmethod
	def from_configfile(cls, configfile=ROBOT_CONFIG_FILE):
		'''Get axis parameters from configfile'''
		with open(configfile) as f:
			return cls.from_config(json.load(f))
			
	@classmethod
	def from_config(cls, config):
		'''Load robot parameters'''

		if 'axis' in config['devices']['X']:
			xaxis = config['devices']['X']['axis']
		else:
			xaxis = DEFAULT_XYZ_AXIS
			
		if 'axis' in config['devices']['Y']:
			yaxis = config['devices']['Y']['axis']
		else:
			yaxis = DEFAULT_XYZ_AXIS

		if 'axis' in config['devices']['Z']:
			zaxis = config['devices']['Z']['axis']
		else:
			zaxis = DEFAULT_XYZ_AXIS

		if 'axis' in config['devices']['P']:
			paxis = config['devices']['P']['axis']
		else:
			paxis = DEFAULT_P_AXIS
			
		if 'axis' in config['devices']['S']:
			saxis = config['devices']['S']['axis']
		else:
			saxis = DEFAULT_S_AXIS
			
		return cls(config, xaxis, yaxis, zaxis, paxis, saxis)

	def arena_from_configfile(self, configfile=ARENA_CONFIG_FILE):
		'''Load arena parameters from configfile'''
		with open(configfile) as f:
			return json.load(f)

	def set_as_attributes(self, dictionary):
		'''Set key:item pairs as attributes within Robot class'''
		for name, item in dictionary.items():
			if hasattr(self, name):
				self.logger.warning("Object named {} is already a reserved attribute, please change name".format(pump_name))
			else:
				setattr(self, name, item)

	def extract_dict_from_dict(self, dict_dict, key):
		'''Copy dict from dict_dict[key] then delete key from dict_dict'''
		new_dict = dict_dict[key]
		del dict_dict[key]
		return new_dict
		
	def extract_rack_from_dict(self, rack_dict, key):
		'''Setup dictionary of TwoDimRack objects using parameters from rack_dict[key] then delete key from rack_dict'''
		rack = {}
		for rack_name, rack_config in rack_dict[key].items():
			if 'labels' in rack_config:
				labels = rack_config['labels']
			else:
				labels = {}
			if 'cycle' in rack_config:
				cycle = rack_config['cycle']
			else:
				cycle = True
			rack[rack_name] = TwoDimRack(rack_config['xy'], rack_config['xyz0'], rack_config['dxyz'], labels, cycle)
		del rack_dict[key]
		return rack


    ## BASIC FUNCTIONS
	def home(self):
		'''Homes xyz axes of robot'''
		self.z.home()
		self.xy.home()

	def move_to(self, xyz, wait=True):
		'''Moves to xyz coordinates with first xy then z'''
		self.z.move_to(xyz[2], wait=wait)
		self.xy.move_to([xyz[0],xyz[1]], wait=True)

	def move_to_firstxy(self, xyz, wait=True):
		'''Moves to xyz coordinates with first xy then z'''
		self.xy.move_to([xyz[0],xyz[1]], wait=True)
		self.z.move_to(xyz[2], wait=wait)

	def move_to_firstz(self, xyz, wait=True):
		'''Moves to xyz coordinates with first xy then z'''
		self.z.move_to(xyz[2], wait=wait)
		self.xy.move_to([xyz[0],xyz[1]], wait=True)

	## WELL FUNCTIONS
	def move_to_well(self, well_index=None, wellplate='wellplate1', tool='pipette'):
		'''Get coordinates of well at index and move there  (index can also be label)'''
		'''well_index=None -> use current index'''
		wx,wy,wz = self.wellplates[wellplate].get_coordinates(well_index)
		x = wx + self.tools[tool][0]
		y = wy + self.tools[tool][1]
		z = wz + self.tools[tool][2]
		self.move_to([x, y, z], wait=True)

	def aspirate_from_well(self, volume, well_index=None, wellplate='wellplate1', tool='pipette'):
		'''Move to well and aspirate volume'''
		self.move_to_well(well_index, wellplate, tool)
		self.z.move(self.liquid_height)
		self.p.aspirate(volume)
		self.move_to_well(well_index, wellplate, tool)

	def dispense_to_well(self, volume, well_index=None, wellplate='wellplate1', tool='pipette'):
		'''Move to well and dispense volume'''
		self.move_to_well(well_index, wellplate, tool)
		self.p.dispense(volume)

	## RESERVOIR FUNCTIONS
	def aspirate_from_reservoir(self, volume, reservoir, tool='pipette'):
		'''Move to reservoir and aspirate volume'''
		if reservoir in self.arena:
			x = self.arena[reservoir][0] + self.tools[tool][0]
			y = self.arena[reservoir][1] + self.tools[tool][1]
			z = self.arena[reservoir][2] + self.tools[tool][2]
			self.z.move_to(0)
			self.xy.move_to([x, y], wait=True)
			self.z.move(self.liquid_height)
			self.p.aspirate(volume)
			self.z.move(z)
		else:
			raise Exception("{} not in arena".format(reservoir))

	## TIP FUNCTIONS
	def dispose_tip(self, tool='pipette'):
		'''Dispose of current tip'''
		self.z.move_to(0)
		ox = self.arena['tip_bin_opening'][0] + self.tools[tool][0]
		oy = self.arena['tip_bin_opening'][1] + self.tools[tool][1]
		oz = self.arena['tip_bin_opening'][2] + self.tools[tool][2]
		self.move_to([ox, oy, oz], wait=True)
		ex = self.arena['tip_bin_ending'][0] + self.tools[tool][0]
		ey = self.arena['tip_bin_ending'][1] + self.tools[tool][1]
		ez = self.arena['tip_bin_ending'][2] + self.tools[tool][2]
		self.move_to([ex, ey, ez], wait=True)

	def collect_tip(self, tool='pipette', tiprack='tiprack1'):
		'''Collect tip with EMPTY adapter'''
		tip_index = self.tipracks[tiprack].next_index()
		tx,ty,tz = self.tipracks[tiprack].get_coordinates(tip_index)
		x = tx + self.tools[tool][0]
		y = ty + self.tools[tool][1]
		z = tz + self.tools[tool][2]
		self.z.move_to(0)
		self.move_to([x, y, z], wait=True)
		self.z.move_to(0)

	def change_tip(self):
		'''Dipose of and collect new tip'''
		self.dispose_tip()
		self.z.move_to(0)
		self.collect_tip()
		self.z.move_to(0)
