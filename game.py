"""This module contains the GameOfLifeSim class

This class is responsible for the simulation of the game of life
It controls pygame so that the simulation can be displayed on the screen

It attempts to use the C extension if it is available, otherwise it uses a python implementation.

Both implementations utilize numpy's stride manipulation to speed up the neighbor summation.

The python implementation is around 2 times slower than the C implementation.
"""
import time
import pygame
import numpy as np

from gol_step import gol_c_numpy_api as game_of_life_step



class GameOfLifeSim:
	"""Game of life simulator class
	This class is responsible for the simulation of the game of life
	It controls pygame so that the simulation can be displayed on the screen
	That means no other pygame should be used simultaneously.
	"""
	# offset from top left corner in pixels
	_offset_x = 0
	_offset_y = 0
	# size of the board in cells
	_width = 1200
	_height = 800
	_scale = 1
	_last_frame = 0
	_board = None
	_frame_number = 0
	_frame_time = 0
	_min_loop_wait = 1
	_last_loop_time = 0
	_paused = False
	_game_tick = 0

	def __init__(self, width=None, height=None, display_size=None, board=None, step_function: callable = game_of_life_step) -> None:
		self.step_function = step_function
		if board is not None:
			self._width = board.shape[0]
			self._height = board.shape[1]
			self._board = board
		elif width is not None and height is not None:
			self._width = width
			self._height = height
			self._board = np.random.randint(0, 2, size=(self._width,self._height), dtype=np.uint8)
		else:
			raise ValueError('either width and height or board must be specified')
		if display_size is None:
			self.display_size = (self._width, self._height)
		else:
			self.display_size = display_size
		self._board = np.pad(self._board, 1, mode='constant', constant_values=0)
		self.running = False
		self.display = pygame.display.set_mode(size=self.display_size)
		self._last_loop_time = time.time()

	def __enter__(self):
		self._init()
		return self._loop
	
	def __exit__(self, exc_type, exc_value, traceback):
		self._close()


	def get_prescaler(self):
		"""Returns the prescaler that the board
		needs to be scaled by to fit the screen"""
		return min(self.display_size[0]/self._width, self.display_size[1]/self._height)

	def handle_pygame_events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4:
					self.zoom_out(event.pos)
				if event.button == 5:
					self.zoom_in(event.pos)
			if event.type == pygame.MOUSEMOTION:
				if event.buttons[0]:
					self.delta_move(*event.rel)
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					self.running = False
				elif event.key == pygame.K_SPACE:
					self._board = self.step_function(self._board)
				elif event.key == pygame.K_COMMA:
					self._min_loop_wait *= 2
					print('Target fps: %3.3f' % (1/self._min_loop_wait))
				elif event.key == pygame.K_PERIOD:
					self._min_loop_wait /= 2
					print('Target fps: %3.3f' % (1/self._min_loop_wait))
				elif event.key == pygame.K_p:
					if self._paused:
						self._last_loop_time = time.time()
						print('Unpaused')
					else:
						print('Paused')
					self._paused = not self._paused

	def _loop(self):
		"""Main loop of the game of life simulation
		
		This function should be called repeatedly without much delay to run the simulation
		
		init() should be called before the first call to loop()
		
		close() should be called after the last call to loop()
		"""
		self.handle_pygame_events()
		
		# calculate the time since the last frame
		tim = time.time()
		delta_time = tim-self._last_loop_time
		if delta_time > self._min_loop_wait and not self._paused:
			self._board = self.step_function(self._board)
			self._last_loop_time = self._last_loop_time + self._min_loop_wait
			self._game_tick += 1

		# size of the visible board in cells
		calc_width = round(self._width*self._scale)
		calc_height = round(self._height*self._scale)
		# offset of the visible board in cells
		calc_offset_x = round(self._offset_x*self._scale)
		calc_offset_y = round(self._offset_y*self._scale)

		# crop the board to the visible area
		cropped_board = self._board[calc_offset_x:calc_offset_x+calc_width, calc_offset_y:calc_offset_y+calc_height]
		# convert to surface of black and white pixels
		surf = pygame.surfarray.make_surface(cropped_board*255)
		# scale the surface to fit the screen
		surf = pygame.transform.scale_by(surf, 1/(self._scale/self.get_prescaler()))
		
		# fill the screen with gray to prevent artifacts
		self.display.fill((0,0,0))

		# draw the surface
		self.display.blit(surf, (0,0), (0,0,self.display_size[0], self.display_size[1]))

		# wait for the next frame, if necessary
		tim = time.time()
		self._last_frame = tim
		#self.frame_time += delta_time
		self._frame_number += 1
		if self._frame_number == 1000:
			print('fps: %3.3f' % (self._frame_number/(tim-self._frame_time)))
			self._frame_number = 0
			self._frame_time = tim

		pygame.display.update()
		return self.running

	def _init(self):
		"""Initializes pygame and the game of life simulation"""
		pygame.init()
		self.display = pygame.display.set_mode(size=self.display_size)
		self._last_frame = time.time()
		self.running = True
		self._game_tick = 0
	
	def _close(self):
		"""Closes pygame and the game of life simulation"""
		pygame.quit()
		self.running = False


	def start(self):
		"""Starts the game of life simulation and runs the main loop until the window is closed
		Alternatively, use init(), loop(), and close() to control the simulation manually.

		"""
		self._init()
		while self.running:
			self._loop()
		self._close()
	

	def delta_move(self, x, y):
		"""Moves the offset by a delta
		The delta is in display pixels
		"""
		prescaler = self.get_prescaler()
		self._offset_x -= x/prescaler
		self._offset_y -= y/prescaler
		self.clamp_offset()
	
	def clamp_offset(self):
		"""Clamps the offset to the visible area
		This is necessary to constrain the surface to the screen,
		otherwise not all of the pixels would be redrawn, resulting in artifacts
		"""
		self._offset_x = max(0, self._offset_x)
		self._offset_y = max(0, self._offset_y)
		cell_offset_x = self._offset_x*self._scale
		cell_offset_y = self._offset_y*self._scale
		cell_offset_x = min(cell_offset_x, self._width-self._width*self._scale)
		cell_offset_y = min(cell_offset_y, self._height-self._height*self._scale)
		self._offset_x = (cell_offset_x/self._scale)
		self._offset_y = (cell_offset_y/self._scale)


	def zoom_in(self, pos):
		"""Zooms in around a point"""
		pr_scale = self._scale
		self._scale *= 1.05
		# clamp scale
		if self._scale>1:
			self._scale = 1
		factor = pr_scale/self._scale
		self.scale_offset_around(factor, pos)
		

	def zoom_out(self, pos):
		"""Zooms out around a point"""
		pr_scale = self._scale
		self._scale /= 1.05
		# clamp scale
		if self._scale<1/16:
			self._scale = 1/16
		factor = pr_scale/self._scale
		self.scale_offset_around(factor, pos)


	def scale_offset_around(self, factor, pos):
		"""Scales the offset by a factor around a point"""
		self._offset_x = ((self._offset_x+pos[0])*factor)-pos[0]
		self._offset_y = ((self._offset_y+pos[1])*factor)-pos[1]
		self.clamp_offset()

	def set_frame_rate(self, fps):
		"""Sets the target frame rate"""
		self._min_loop_wait = 1/fps
	
	def get_current_tick(self):
		"""Returns the current game tick"""
		return self._game_tick
