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
		except Exception as e:
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
	GameOfLifeSim(1200, 800).start()
	root.deiconify()

def run_pattern_maker():
	root.withdraw()
	pattern = MakeLife(80, 50, (1200, 800)).start()
	file_name = filedialog.asksaveasfilename(initialdir=os.getcwd(), defaultextension='.rle', filetypes=[('RLE files', '*.rle')])
	if file_name:
		save_state(file_name, pattern)
	root.deiconify()

if __name__ == '__main__':
	root.title("Game of Life")
	root.geometry("300x300")
	width_input = tk.Entry(root)
	width_input.pack(fill='both')
	height_input = tk.Entry(root)
	height_input.pack(fill='both')
	tk.Button(root, text="Select file", command=run_game_from_file).pack(fill='both')
	tk.Button(root, text="Random layout", command=run_game_from_random).pack(fill='both')
	tk.Button(root, text="Make pattern", command=run_pattern_maker).pack(fill='both')
	tk.Button(root, text="Quit", command=root.quit).pack(fill='both')
	root.mainloop()
else:
	print("this main.py is not meant to be imported")
	