"""
    coding: UTF-8
    Python 2.7

    pipette.py

    Jonathan Grizou, The Cronin Group, University of Glasgow

    Stepper motor pipetting system
	
	July 2018:
	Slightly modified for replacement 3D printed pipette
"""

class Pipette(object):

    def __init__(self, axis_device, empty_level, total_volume):
        # axis device should be calibrated in uL units, with min and max well defined for security, even if this layer adds additonal security
        self.axis = axis_device
        self.empty_level = empty_level
        self.total_volume = total_volume
        self.current_volume = 0
        #self.home_volume = -10000 # uL
        self.init()
        self.axis.linear_actuator.set_current_position(0)

    def home(self, wait=True):
        #home_move_position = self.volume_to_position(self.home_volume)
        #home_move_step = self.axis.position_to_step(home_move_position)
        #self.axis.linear_actuator.move(home_move_step, wait=True)
        #self.axis.linear_actuator.set_current_position(0)
		self.axis.home()
		self.current_volume = 0

    def init(self):
		self.axis.initialize()
		self.current_volume = 0

    def is_empty(self):
        return self.current_volume == 0

    def volume_to_position(self, volume_in_uL):
        return self.empty_level + volume_in_uL

    @property
    def remaining_volume(self):
        return self.total_volume - self.current_volume

    def is_volume_valid(self, volume_in_uL):
        return 0 <= volume_in_uL <= self.total_volume

    def wait_until_idle(self):
        self.axis.wait_until_idle()

    def go_to_volume(self, volume_in_uL, wait=True):
        # hard security here, we do not handle wrong user behavior and just throw an exception
        if not self.is_volume_valid(volume_in_uL):
            raise Exception('Volume {} is not valid'.format(volume_in_uL))

        # we wait in case a previous command did not finished
        self.wait_until_idle()

        position = self.volume_to_position(volume_in_uL)
        self.axis.move_to(position, wait=wait, force=True)
        self.current_volume = volume_in_uL

    def aspirate(self, volume_in_uL, wait=True):
		if volume_in_uL <= (self.total_volume - self.current_volume):
			self.go_to_volume(self.current_volume + volume_in_uL, wait=wait)
			return 'Volume {}uL aspirated into pipette'.format(volume_in_uL)
		else:
			raise Exception('Not enough space in pipette to aspirate {}uL'.format(volume_in_uL))

    def dispense(self, volume_in_uL, wait=True):
        if volume_in_uL <= self.current_volume:
            self.go_to_volume(self.current_volume - volume_in_uL, wait=wait)
            return 'Volume {}uL dispensed from pipette'.format(volume_in_uL)
        else:
            raise Exception('Not enough in pipette to dispense {}uL'.format(volume_in_uL))
