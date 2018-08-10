"""
    coding: UTF-8
    Python 2.7

    Shaker.py
	
	July 2018:
	New class based off the axis class. Modified to suit a rotational device rather than a linear device.
"""

class Shaker(object):

	def __init__(self, linear_actuator, deg_per_step=1, min_position=-1000, max_position=1000):
		self.linear_actuator = linear_actuator
		self.deg_per_step = float(deg_per_step)
		self.min_position = float(min_position)
		self.max_position = float(max_position)
		self.current_position = 0
		self.initialized = True
		#self.initialize

	def initialize(self):
		"""
		Initialises the axis.aa
		"""

		self.home(wait=True)

	def is_initialized(self):
		"""
		Check for initialisation.

		Returns:
			self.initialized (bool): Initialisation status

		"""

		return self.initialized

	def angle_to_step(self, angle_in_degrees):
		"""
		Converts position to steps.

		Args:
			position_in_unit (int): Position in Units.

		Returns:
			n_steps (int): Number of steps.

		"""

		n_steps = angle_in_degrees / self.deg_per_step
		return int(round(n_steps))

	def is_moving(self):
		"""
		Check for axis movement.

		Returns:
			self.linear_actuator.is_moving (bool): The actuator movement status.

		"""

		return self.linear_actuator.is_moving()

	def wait_until_idle(self):
		"""
		Waits until the linear actuator is idle.
		"""

		self.linear_actuator.wait_until_idle()

	def home(self, wait=True):
		"""
		Returns the actuator to the home position.

		Args:
			wait (bool): Wait until the actuator is idle, default set to True

		"""

		self.linear_actuator.home(wait=wait)
		self.initialized = True

	def zero(self):
		#round the current angle to the nearest multiple of 360
		nearest_home = int(360 * round(float(self.current_position)/360))
		#move to this angle e.g. ...-720, -360, 0, 360, 720...
		self.rotate_to(nearest_home)
		#make this the new zero point
		self.current_position = 0

	def rotate_to(self, angle_in_degrees, wait=True, force=False):
		"""
		Moves the linear actuator to a set position.

		Args:
			position_in_unit (int): Position to move to.

			wait (bool): Wait until the actuator is idle, default set to True.

			force (bool): Force the movement, default set to False.

		"""
		self.wait_until_idle
		if self.is_initialized() or force==True:
			n_steps = self.angle_to_step(angle_in_degrees)
			self.linear_actuator.move_to(n_steps, wait=wait)
			self.current_position = angle_in_degrees

	def rotate(self, delta_angle_in_degrees, wait=True, force=False):
		"""
		Moves the linear actuator.

		Args:
			delta_position_in_unit (int): The amount to move.

			wait (bool): Wait until the linear actuator is idle, default set to True.

			force (bool):Force the movement, default set to False.

		"""

		#current_position = self.get_current_position()
		self.rotate_to(self.current_position + delta_angle_in_degrees, wait=wait, force=force)
		
	def speed(self, deg_per_sec):
		self.wait_until_idle
		step_per_sec = self.angle_to_step(deg_per_sec)
		self.linear_actuator.set_max_speed(step_per_sec)
		
	def acceleration(self, deg_per_sec_sq):
		self.wait_until_idle
		step_per_sec_sq = self.angle_to_step(deg_per_sec_sq)
		self.linear_actuator.set_acceleration(step_per_sec_sq)

	def stop(self):
		"""
		Stops the linear actuator.
		"""
		self.linear_actuator.stop()