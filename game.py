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

from gol_step import gol_c as game_of_life_step

class GameOfLifeSim:
	"""Game of life simulator class
	This class is responsible for the simulation of the game of life
	It controls pygame so that the simulation can be displayed on the screen
	That means no other pygame should be used simultaneously.
	"""
	# offset from top left corner in pixels
	offset_x = 0
	offset_y = 0
	# size of the board in cells
	width = 1200
	height = 800
	scale = 1
	last_frame = 0
	board = None
	frame_number = 0
	frame_time = 0
	_min_loop_wait = 1
	_last_loop_time = 0
	_paused = False

	def __init__(self, width=None, height=None, display_size=None, board=None, step_function: callable = game_of_life_step) -> None:
		self.step_function = step_function
		if board is not None:
			self.width = board.shape[0]
			self.height = board.shape[1]
			self.board = board
		elif width is not None and height is not None:
			self.width = width
			self.height = height
			self.board = np.random.randint(0, 2, size=(self.width,self.height), dtype=np.uint8)
		else:
			raise ValueError('either width and height or board must be specified')
		if display_size is None:
			self.display_size = (self.width, self.height)
		else:
			self.display_size = display_size
		self.board = np.pad(self.board, 1, mode='constant', constant_values=0)
		self.running = False
		self.display = pygame.display.set_mode(size=self.display_size)
		self._last_loop_time = time.time()

	def get_prescaler(self):
		"""Returns the prescaler that the board
		needs to be scaled by to fit the screen"""
		return min(self.display_size[0]/self.width, self.display_size[1]/self.height)

	def loop(self):
		"""Main loop of the game of life"""
		# calculate the time since the last frame
		tim = time.time()
		delta_time = tim-self._last_loop_time
		if delta_time > self._min_loop_wait and not self._paused:
			self.board = self.step_function(self.board)
			self._last_loop_time = self._last_loop_time + self._min_loop_wait

		# size of the visible board in cells
		calc_width = round(self.width*self.scale)
		calc_height = round(self.height*self.scale)
		# offset of the visible board in cells
		calc_offset_x = round(self.offset_x*self.scale)
		calc_offset_y = round(self.offset_y*self.scale)

		# crop the board to the visible area
		cropped_board = self.board[calc_offset_x:calc_offset_x+calc_width, calc_offset_y:calc_offset_y+calc_height]
		# convert to surface of black and white pixels
		surf = pygame.surfarray.make_surface(cropped_board*255)
		# scale the surface to fit the screen
		surf = pygame.transform.scale_by(surf, 1/(self.scale/self.get_prescaler()))
		
		# fill the screen with gray to prevent artifacts
		self.display.fill((0,0,0))

		# draw the surface
		self.display.blit(surf, (0,0), (0,0,self.display_size[0], self.display_size[1]))

		# wait for the next frame, if necessary
		tim = time.time()
		self.last_frame = tim
		#self.frame_time += delta_time
		self.frame_number += 1
		if self.frame_number == 1000:
			print('fps: %3.3f' % (self.frame_number/(tim-self.frame_time)))
			self.frame_number = 0
			self.frame_time = tim



	def start(self):
		"""Starts the game of life simulation"""
		
		pygame.init()
		self.display = pygame.display.set_mode(size=self.display_size)
		self.last_frame = time.time()

		self.running = True
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				if event.type == pygame.MOUSEBUTTONDOWN:
					#print(event.button)
					#print(event.pos)
					if event.button == 4:
						self.zoomOut(event.pos)
					if event.button == 5:
						self.zoomIn(event.pos)
				if event.type == pygame.MOUSEMOTION:
					#print(event)
					if event.buttons[0]:
						self.delta_move(*event.rel)
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.running = False
					if event.key == pygame.K_SPACE:
						self.board = self.step_function(self.board)
					if event.key == pygame.K_COMMA:
						self._min_loop_wait *= 2
						print('Target fps: %3.3f' % (1/self._min_loop_wait))
					if event.key == pygame.K_PERIOD:
						self._min_loop_wait /= 2
						print('Target fps: %3.3f' % (1/self._min_loop_wait))
					if event.key == pygame.K_p:
						if self._paused:
							self._last_loop_time = time.time()
							print('Unpaused')
						else:
							print('Paused')
						self._paused = not self._paused

			self.loop()
			pygame.display.update()


		pygame.quit()
	

	def delta_move(self, x, y):
		"""Moves the offset by a delta
		The delta is in display pixels
		"""
		prescaler = self.get_prescaler()
		self.offset_x -= x/prescaler
		self.offset_y -= y/prescaler
		self.clampOffset()
	
	def clampOffset(self):
		"""Clamps the offset to the visible area
		This is necessary to constrain the surface to the screen,
		otherwise not all of the pixels would be redrawn, resulting in artifacts
		"""
		self.offset_x = max(0, self.offset_x)
		self.offset_y = max(0, self.offset_y)
		cell_offset_x = self.offset_x*self.scale
		cell_offset_y = self.offset_y*self.scale
		cell_offset_x = min(cell_offset_x, self.width-self.width*self.scale)
		cell_offset_y = min(cell_offset_y, self.height-self.height*self.scale)
		self.offset_x = (cell_offset_x/self.scale)
		self.offset_y = (cell_offset_y/self.scale)


	def zoomIn(self, pos):
		"""Zooms in around a point"""
		pr_scale = self.scale
		self.scale *= 1.05
		# clamp scale
		if self.scale>1:
			self.scale = 1
		factor = pr_scale/self.scale
		self.scale_offset_around(factor, pos)
		

	def zoomOut(self, pos):
		"""Zooms out around a point"""
		pr_scale = self.scale
		self.scale /= 1.05
		# clamp scale
		if self.scale<1/16:
			self.scale = 1/16
		factor = pr_scale/self.scale
		self.scale_offset_around(factor, pos)


	def scale_offset_around(self, factor, pos):
		"""Scales the offset by a factor around a point"""
		self.offset_x = ((self.offset_x+pos[0])*factor)-pos[0]
		self.offset_y = ((self.offset_y+pos[1])*factor)-pos[1]
		self.clampOffset()
