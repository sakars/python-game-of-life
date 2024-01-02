"""This is the main file for the Game of Life. It contains the main loop and the
functions for running the game from a file, random layout or pattern maker.
This is meant to be run, not imported.
"""
import os
import numpy as np
from game import GameOfLifeSim
import tkinter as tk
from tkinter import filedialog
from state_loader import load_data, save_state
from make_life import MakeLife

root = tk.Tk()
width_input = None
height_input = None

def run_game_from_file():
	# Open file dialog
	file_path = filedialog.askopenfilename(initialdir=os.getcwd())
	game = None
	# Check if a file was selected
	if file_path:
		# Process the selected file
		print("Selected file:", file_path)
		try:
			game = GameOfLifeSim(board=load_data(file_name=file_path))
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
	GameOfLifeSim(int(width_input.get()), int(height_input.get())).start()
	root.deiconify()

def run_pattern_maker():
	resolution = (int(width_input.get()), int(height_input.get()))
	root.withdraw()
	pattern = MakeLife(80, 50, resolution).start()
	file_name = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension='.rle', filetypes=[('RLE files', '*.rle')])
	if file_name:
		save_state(file_name, pattern)
	root.deiconify()

def run_edit_pattern():
	resolution = (int(width_input.get()), int(height_input.get()))
	root.withdraw()
	file_path = filedialog.askopenfilename(initialdir=os.getcwd(), filetypes=[('RLE files', '*.rle')])
	if file_path:
		pattern = load_data(file_name=file_path, min_size=(80, 50))
		pattern = MakeLife(pattern.shape[0], pattern.shape[1], resolution, pattern).start()
		save_state(file_path, pattern)
	root.deiconify()

if __name__ == '__main__':
	root.title("Game of Life")
	root.geometry("300x300")
	tk.Label(root, text="Resolution").pack(fill='both')
	res_frame = tk.Frame(root)
	res_frame.pack(fill='both')
	width_input = tk.Entry(res_frame)
	width_input.pack(side='left', fill='both', expand=True)
	width_input.insert(0, "1200")
	tk.Label(res_frame, text="X").pack(side='left', fill='both', expand=False)
	height_input = tk.Entry(res_frame)
	height_input.pack(side = 'right',fill='both', expand=True)
	height_input.insert(0, "800")
	tk.Button(root, text="Select file", command=run_game_from_file).pack(fill='both')
	tk.Button(root, text="Random layout", command=run_game_from_random).pack(fill='both')
	tk.Button(root, text="Make pattern", command=run_pattern_maker).pack(fill='both')
	tk.Button(root, text="Edit pattern", command=run_edit_pattern).pack(fill='both')
	tk.Button(root, text="Quit", command=root.quit).pack(fill='both')
	root.mainloop()
else:
	print("this main.py is not meant to be imported")
	