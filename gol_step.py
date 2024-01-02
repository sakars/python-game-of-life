
import numpy as np

def gol_py_simple(board:np.ndarray) -> np.ndarray:
	"""This is the old version of the neighbour summation, it is slower but slightly easier to understand"""
		
	# create a 4d array with the 3x3 neighborhood of each cell in the board
	# This is just a view of the board, so no additional memory is used
	conv = np.lib.stride_tricks.as_strided(board, shape=(board.shape[0]-2, board.shape[1]-2,3,3),
		strides=(board.strides[0], board.strides[1], board.strides[0], board.strides[1]))
	# sum the neighborhood of each cell resulting in a 2d array with the amount of neighbors of each cell
	conv_sum = np.pad(np.sum(conv, axis=(2,3)) - board[1:-1,1:-1], 1, mode='constant', constant_values=0)
	
	# apply the game of life rules
	alive = board == 1
	is_three = conv_sum == 3
	is_two = conv_sum == 2
	board[alive & (np.logical_not(is_two | is_three))] = 0
	board[np.logical_not(alive) & is_three] = 1
	return board


def gol_py_partial_sums(board:np.ndarray) -> np.ndarray:
	# create a 3d array with the 3x1 neighborhood of each non-border cell in the board
	conv = np.lib.stride_tricks.as_strided(board, shape=(board.shape[0]-2, board.shape[1],3),
		strides=(board.strides[0], board.strides[1], board.strides[0]))
	# sum the neighborhood of each cell resulting in a 2d array with the amount of alive horizontal neighbors of each cell
	conv_sum: np.ndarray = np.sum(conv, axis=2, dtype=np.uint8)

	# create a 3d array with the 3x3 neighborhood of each non-border cell in the board
	# because we already have the horizontal neighbors, the 1x3 neighborhood represents the whole 3x3 neighborhood
	conv_sum = np.lib.stride_tricks.as_strided(conv_sum, shape=(conv_sum.shape[0],conv_sum.shape[1]-2,3),
		strides=(conv_sum.strides[0], conv_sum.strides[1], conv_sum.strides[1]))
	
	# sum the neighborhood of each cell resulting in a 2d array with the amount of total alive neighbors of each cell
	conv_sum = np.pad(np.sum(conv_sum, axis=2) - board[1:-1,1:-1], 1, mode='constant', constant_values=0)
	
	# apply the game of life rules
	alive = board == 1
	is_three = conv_sum == 3
	is_two = conv_sum == 2
	board[alive & (np.logical_not(is_two | is_three))] = 0
	board[np.logical_not(alive) & is_three] = 1
	return board

# attempt to import the C extension
try:
	import GOL
	gol_c = GOL.step_NpArr
except ImportError:
	print("C extension not found, using python implementation")
	gol_c = gol_py_partial_sums

