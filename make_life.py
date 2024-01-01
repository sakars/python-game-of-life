
import pygame
import numpy as np
import math
from game import GameOfLifeSim

class MakeLife:
	"""Game of life creation tool class
	This class is responsible for handling the window
	that allows the user to create a game of life pattern
	
	It controls pygame so that the simulation can be displayed on the screen
	That means no other pygame should be used simultaneously.

	It can also run the game of life on the current board for testing purposes
	"""
	board = None
	width = None
	height = None
	display = None
	running = None
	display_size = None
	def __init__(self, width:int, height:int, display_size: (int, int)) -> None:
		pygame.init()
		self.width = width
		self.height = height
		self.board = np.zeros((self.width, self.height), dtype=np.uint8)
		self.display = pygame.display.set_mode(display_size)
		self.running = False
		self.display_size = display_size

	def loop(self):
		"""Main loop of the game of life creation tool"""
		while self.running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						board_index = self.to_indices(event.pos)
						#print(event.pos, board_index)
						self.board[board_index[0], board_index[1]] = 1
						#print(self.board)
					elif event.button == 3:
						board_index = self.to_indices(event.pos)
						self.board[board_index[0],board_index[1]] = 0
						#print(self.board)
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN:
						self.running = False
					elif event.key == pygame.K_r:
						# Run the game of life on the current board
						self.run_life()
			
			left_click, _, right_click = pygame.mouse.get_pressed()
			if left_click:
				board_index = self.to_indices(pygame.mouse.get_pos())
				self.board[board_index[0], board_index[1]] = 1
			elif right_click:
				board_index = self.to_indices(pygame.mouse.get_pos())
				self.board[board_index[0],board_index[1]] = 0


			self.display.fill((0,0,0))
			pixelsPerCell = (self.display_size[0]/self.width, self.display_size[1]/self.height)
			surf = pygame.surface.Surface(self.display_size)
			for i in range(self.width):
				for j in range(self.height):
					if self.board[i,j] == 1:
						pygame.draw.rect(surf,(255,255,255),
					   		(
								i*pixelsPerCell[0],
								j*pixelsPerCell[1],
								pixelsPerCell[0],
								pixelsPerCell[1]
							))
			self.display.blit(surf, (0,0))
			pygame.display.update()
		pygame.quit()
		return self.board
	
	def start(self):
		"""Starts the game of life creation tool"""
		self.running = True
		return self.loop()
	
	def to_indices(self, pos):
		"""Converts a position on the screen to the corresponding indices on the board"""
		unclamped_pos = (
			math.floor(pos[0]/self.display_size[0]*self.width),
			math.floor(pos[1]/self.display_size[1]*self.height)
			)
		return (
			min(max(unclamped_pos[0], 0), self.width-1),
			min(max(unclamped_pos[1], 0), self.height-1)
			)
	

	def run_life(self):
		"""Run the game of life on the current board
		
		This function halts the creation tool and runs the game of life on the current board
		
		A new window is opened to display the game of life

		After the game of life is finished, the creation tool is resumed
		"""
		if self.running:
			pygame.display.update()
			pygame.quit()
		padded_board =np.array(self.board)# np.pad(self.board, 20, mode='constant')
		game = GameOfLifeSim(board=padded_board, display_size=self.display_size)
		game.start()
		if self.running:
			pygame.init()
			self.display = pygame.display.set_mode(self.display_size)
			self.running = True

