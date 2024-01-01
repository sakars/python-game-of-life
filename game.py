"""This module contains the GameOfLifeSim class

This class is responsible for the simulation of the game of life
It controls pygame so that the simulation can be displayed on the screen

It attempts to use the C extension if it is available, otherwise it uses a python implementation.

Both implementations utilize numpy's stride manipulation to speed up the neighbor summation.

The python implementation is just under 3 times slower than the C implementation.
"""
import time
import pygame
import numpy as np

# try to import the C extension if USE_C is True
USE_C = True
if USE_C:
	try:
		import GOL
	except ImportError:
		USE_C = False
		print("C extension not found, using python implementation")

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
	min_wait = 0
	last_frame = 0
	board = None
	frame_number = 0
	frame_time = 0
	def __init__(self, width=None, height=None, display_size=None, board=None) -> None:
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
	
	def get_prescaler(self):
		"""Returns the prescaler that the board
		needs to be scaled by to fit the screen"""
		return min(self.display_size[0]/self.width, self.display_size[1]/self.height)

	def loop(self):
		"""Main loop of the game of life"""
		
		## This is the old version of the neighbour summation, it is slower but slightly easier to understand
		
		# create a 4d array with the 3x3 neighborhood of each cell in the board
		# This is just a view of the board, so no additional memory is used
		# conv = np.lib.stride_tricks.as_strided(self.board, shape=(self.board.shape[0]-2,self.board.shape[1]-2,3,3),
		# 	strides=(self.board.strides[0], self.board.strides[1], self.board.strides[0], self.board.strides[1]))
		# # sum the neighborhood of each cell resulting in a 2d array with the amount of neighbors of each cell
		# conv_sum = np.pad(np.sum(conv, axis=(2,3)) - self.board[1:-1,1:-1], 1, mode='constant', constant_values=0)
		
		if USE_C:
			self.board = GOL.step_NpArr(self.board)
		else:
			# create a 3d array with the 3x1 neighborhood of each non-border cell in the board
			conv = np.lib.stride_tricks.as_strided(self.board, shape=(self.board.shape[0]-2,self.board.shape[1],3),
				strides=(self.board.strides[0], self.board.strides[1], self.board.strides[0]))
			# sum the neighborhood of each cell resulting in a 2d array with the amount of alive horizontal neighbors of each cell
			conv_sum = np.sum(conv, axis=2, dtype=np.uint8)

			# create a 3d array with the 3x3 neighborhood of each non-border cell in the board
			# because we already have the horizontal neighbors, the 1x3 neighborhood represents the whole 3x3 neighborhood
			conv_sum = np.lib.stride_tricks.as_strided(conv_sum, shape=(conv_sum.shape[0],conv_sum.shape[1]-2,3),
				strides=(conv_sum.strides[0], conv_sum.strides[1], conv_sum.strides[1]))
			
			# sum the neighborhood of each cell resulting in a 2d array with the amount of total alive neighbors of each cell
			conv_sum = np.pad(np.sum(conv_sum, axis=2) - self.board[1:-1,1:-1], 1, mode='constant', constant_values=0)
			
			# apply the game of life rules
			alive = self.board == 1
			is_three = conv_sum == 3
			is_two = conv_sum == 2
			self.board[alive & (np.logical_not(is_two | is_three))] = 0
			self.board[np.logical_not(alive) & is_three] = 1
		
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
		#self.display.fill((100,100,100))

		# draw the surface
		self.display.blit(surf, (0,0), (0,0,self.display_size[0], self.display_size[1]))

		# wait for the next frame, if necessary
		tim = time.time()
		delta_time = tim - self.last_frame
		if delta_time < self.min_wait:
			time.sleep(self.min_wait - delta_time)
		#time.sleep(3)
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

		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
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
