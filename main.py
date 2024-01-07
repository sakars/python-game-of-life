"""This is the main file for the Game of Life. It contains the main loop and the
functions for running the game from a file, random layout or pattern maker.
This is meant to be run, not imported.
"""
import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from game import GameOfLifeSim
from state_loader import load_data, save_state
from make_life import MakeLife
from gol_step import (HAS_C_EXTENSION, gol_py_partial_sums, gol_py_simple, gol_py_trivial,
	gol_py_slooow, gol_c_pylist_multithread, gol_c_numpy_api)

root = tk.Tk()
width_res_input = None
height_res_input = None
width_board_input = None
height_board_input = None


def fetch_resolution():
	"""Fetches the resolution from the GUI"""
	width = int(width_res_input.get())
	height = int(height_res_input.get())
	width = max(width, 10)
	height = max(height, 10)
	return (width, height)

def fetch_board_size():
	"""Fetches the board size from the GUI"""
	width = int(width_board_input.get())
	height = int(height_board_input.get())
	width = max(width, 5)
	height = max(height, 5)
	return (width, height)

def run_game_from_file():
	# Open file dialog
	file_path = filedialog.askopenfilename(initialdir=os.getcwd())
	game = None
	# Check if a file was selected
	if file_path:
		# Process the selected file
		print("Selected file:", file_path)
		try:
			game = GameOfLifeSim(
				board=load_data(
					file_name=file_path, 
					min_size=fetch_board_size()
					),
				display_size=fetch_resolution()
				)
		except FileNotFoundError as e:
			print("Error loading file:", e)
			tk.messagebox.showerror("Error", "Error loading file")
		except ValueError as e:
			print("Error loading file:", e)
			tk.messagebox.showerror("Error", "Error loading file")
		except FileExistsError as e:
			print("Error loading file:", e)
			tk.messagebox.showerror("Error", "Error loading file")
	else:
		print("No file selected")
		tk.messagebox.showerror("Error", "No file selected")
	if game is not None:
		root.withdraw()
		game.start()
		root.deiconify()

def run_game_from_random():
	root.withdraw()
	display_size = fetch_resolution()
	board_size = fetch_board_size()
	GameOfLifeSim(board_size[0], board_size[1], display_size=display_size).start()
	root.deiconify()

def run_pattern_maker():
	resolution = fetch_resolution()
	board_size = fetch_board_size()
	root.withdraw()
	pattern = MakeLife(board_size[0], board_size[1], resolution).start()
	file_name = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension='.rle', filetypes=[('RLE files', '*.rle')])
	if file_name:
		save_state(file_name, pattern)
	root.deiconify()

def run_edit_pattern():
	resolution = fetch_resolution()
	board_size = fetch_board_size()
	root.withdraw()
	file_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[('RLE files', '*.rle')])
	if file_path:
		pattern = load_data(file_name=file_path, min_size=board_size)
		pattern = MakeLife(pattern.shape[0], pattern.shape[1], resolution, pattern).start()
		save_state(file_path, pattern)
	root.deiconify()

def run_benchmaster():
	"""This function is used to benchmark the different step functions"""
	root.withdraw()
	steps_to_benchmark = 100
	result_string = f"Benchmark results (time for {steps_to_benchmark} steps):\n"

	game = GameOfLifeSim(width=120, height=80, display_size=(1200,800), step_function=gol_py_slooow)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	result_string += f"- solution of 2 for loops through a list (100x smaller board): {time.time() - start_time}\n"

	game = GameOfLifeSim(width=120, height=80, display_size=(1200, 800), step_function=gol_py_trivial)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	result_string += f"- solution of 2 for loops through a numpy array (100x smaller board): {time.time() - start_time}\n"


	game = GameOfLifeSim(width=1200, height=800, step_function=gol_py_simple)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	result_string += f"- numpy stride tricks: {time.time() - start_time}\n"

	game = GameOfLifeSim(width=1200, height=800, step_function=gol_py_partial_sums)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	result_string += f"- numpy stride tricks with partial sums: {time.time() - start_time}\n"

	if HAS_C_EXTENSION:
		game = GameOfLifeSim(width=1200, height=800, step_function=gol_c_pylist_multithread)
		game.set_frame_rate(10000)
		start_time = time.time()
		with game as tick:
			while game.get_current_tick() < 100:
				tick()
		result_string += f"- C extension with python lists (utilizing partial sums): {time.time() - start_time}\n"


		game = GameOfLifeSim(width=1200, height=800, step_function=gol_c_numpy_api)
		game.set_frame_rate(10000)
		start_time = time.time()
		with game as tick:
			while game.get_current_tick() < 100:
				tick()
		result_string += f"- C extension with numpy arrays (utilizing partial sums): {time.time() - start_time}\n"

	messagebox.showinfo("Benchmark results", result_string)

	root.deiconify()



if __name__ == '__main__':
	if not HAS_C_EXTENSION:
		messagebox.showwarning("C extension not found", "C extension not found, using python implementation as default")
	root.title("Game of Life")
	root.geometry("300x300")
	tk.Label(root, text="Resolution").pack(fill='both')
	res_frame = tk.Frame(root)
	res_frame.pack(fill='both')
	width_res_input = tk.Entry(res_frame)
	width_res_input.pack(side='left', fill='both', expand=True)
	width_res_input.insert(0, "1200")
	tk.Label(res_frame, text="X").pack(side='left', fill='both', expand=False)
	height_res_input = tk.Entry(res_frame)
	height_res_input.pack(side = 'right',fill='both', expand=True)
	height_res_input.insert(0, "800")
	tk.Label(root, text="Board size").pack(fill='both')
	board_frame = tk.Frame(root)
	board_frame.pack(fill='both')
	width_board_input = tk.Entry(board_frame)
	width_board_input.pack(side='left', fill='both', expand=True)
	width_board_input.insert(0, "1200")
	tk.Label(board_frame, text="X").pack(side='left', fill='both', expand=False)
	height_board_input = tk.Entry(board_frame)
	height_board_input.pack(side = 'right',fill='both', expand=True)
	height_board_input.insert(0, "800")
	tk.Button(root, text="Select file", command=run_game_from_file).pack(fill='both')
	tk.Button(root, text="Random layout", command=run_game_from_random).pack(fill='both')
	tk.Button(root, text="Make pattern", command=run_pattern_maker).pack(fill='both')
	tk.Button(root, text="Edit pattern", command=run_edit_pattern).pack(fill='both')
	tk.Button(root, text="Benchmark", command=run_benchmaster).pack(fill='both')
	tk.Button(root, text="Quit", command=root.quit).pack(fill='both')
	root.mainloop()
else:
	print("this main.py is not meant to be imported")
	