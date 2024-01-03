"""This is the main file for the Game of Life. It contains the main loop and the
functions for running the game from a file, random layout or pattern maker.
This is meant to be run, not imported.
"""
import os
from game import GameOfLifeSim
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from state_loader import load_data, save_state
from make_life import MakeLife
from gol_step import *
import time

root = tk.Tk()
width_res_input = None
height_res_input = None
width_board_input = None
height_board_input = None

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
					min_size=(
						int(width_board_input.get()), 
						int(height_board_input.get())
						)
					),
				display_size=(int(width_res_input.get()), int(height_res_input.get()))
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
	display_size = (int(width_res_input.get()), int(height_res_input.get()))
	board_size = (int(width_board_input.get()), int(height_board_input.get()))
	GameOfLifeSim(board_size[0], board_size[1], display_size=display_size).start()
	root.deiconify()

def run_pattern_maker():
	resolution = (int(width_res_input.get()), int(height_res_input.get()))
	board_size = (int(width_board_input.get()), int(height_board_input.get()))
	root.withdraw()
	pattern = MakeLife(board_size[0], board_size[1], resolution).start()
	file_name = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension='.rle', filetypes=[('RLE files', '*.rle')])
	if file_name:
		save_state(file_name, pattern)
	root.deiconify()

def run_edit_pattern():
	resolution = (int(width_res_input.get()), int(height_res_input.get()))
	board_size = (int(width_board_input.get()), int(height_board_input.get()))
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
	result_string = f"Benchmark results for {steps_to_benchmark} steps:\n"

	game = GameOfLifeSim(width=120, height=80, display_size=(1200, 800), step_function=gol_py_trivial)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	result_string += f"- trivial solution of 2 for loops (board is 100x smaller): {time.time() - start_time}\n"
	#print("Time for 100 steps with gol_py_trivial (the board is reduced by 100 times):", time.time() - start_time)


	game = GameOfLifeSim(width=1200, height=800, step_function=gol_py_simple)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	#print("Time for 100 steps with gol_py_simple:", time.time() - start_time)
	result_string += f"- numpy stride tricks: {time.time() - start_time}\n"

	game = GameOfLifeSim(width=1200, height=800, step_function=gol_py_partial_sums)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	#print("Time for 100 steps with gol_py_partial_sums:", time.time() - start_time)
	result_string += f"- numpy stride tricks with partial sums: {time.time() - start_time}\n"


	game = GameOfLifeSim(width=1200, height=800, step_function=gol_c_pylist_multithread)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	#print("Time for 100 steps with gol_c_pylist_multithread:", time.time() - start_time)
	result_string += f"- C extension with python lists (utilizing partial sums): {time.time() - start_time}\n"


	game = GameOfLifeSim(width=1200, height=800, step_function=gol_c_numpy_api)
	game.set_frame_rate(10000)
	start_time = time.time()
	with game as tick:
		while game.get_current_tick() < 100:
			tick()
	#print("Time for 100 steps with gol_c:", time.time() - start_time)
	result_string += f"- C extension with numpy arrays (utilizing partial sums): {time.time() - start_time}\n"

	messagebox.showinfo("Benchmark results", result_string)

	root.deiconify()



if __name__ == '__main__':
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
	width_board_input.insert(0, "120")
	tk.Label(board_frame, text="X").pack(side='left', fill='both', expand=False)
	height_board_input = tk.Entry(board_frame)
	height_board_input.pack(side = 'right',fill='both', expand=True)
	height_board_input.insert(0, "80")
	tk.Button(root, text="Select file", command=run_game_from_file).pack(fill='both')
	tk.Button(root, text="Random layout", command=run_game_from_random).pack(fill='both')
	tk.Button(root, text="Make pattern", command=run_pattern_maker).pack(fill='both')
	tk.Button(root, text="Edit pattern", command=run_edit_pattern).pack(fill='both')
	tk.Button(root, text="Benchmark", command=run_benchmaster).pack(fill='both')
	tk.Button(root, text="Quit", command=root.quit).pack(fill='both')
	root.mainloop()
else:
	print("this main.py is not meant to be imported")
	