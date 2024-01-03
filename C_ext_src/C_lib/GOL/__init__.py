

from . import core
import numpy as np

def step_NpArr(arr:np.ndarray) -> np.ndarray:
	"""Step the game of life for a numpy array.
	Warning: It can modify the array in place.
	Returns the same or a new array with the next step.
	"""
	
	return core.step_NpArr(arr)

def step_list_multithread(arr:list) -> list:
	"""Step the game of life for a list of lists.
	Warning: It can modify the list in place.
	Returns the same or a new list with the next step.
	"""
	return core.step_list_multithread(arr)

def step_NpArr_multithread(arr:np.ndarray) -> np.ndarray:
	"""Step the game of life for a numpy array.
	Warning: It can modify the array in place.
	Returns the same or a new array with the next step.
	"""
	
	return core.step_NpArr_multithread(arr)