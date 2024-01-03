import numpy as np

# State format:
# width,height
# segment_amount
# segment1_x, segment1_y, segment1_width, segment1_height
# segment_data
# segment2_x, segment2_y, segment2_width, segment2_height
# segment_data

def rle_decode(file_name, min_size=(0,0)):
	"""Decodes a RLE file"""
	read_file = open(file_name, 'r', encoding='utf-8')
	state = np.zeros((1200, 800), dtype=np.uint8)
	state_buffer = state
	offset = (0, 0)
	while True:
		line = read_file.readline()
		if line.startswith('!'):
			continue
		elif line.startswith('#'):
			if line[1] == 'R':
				params = line.split(' ')
				# state_buffer = state[int(params[1]):, int(params[2]):]
				offset = (int(params[1]), int(params[2]))
		else:
			break
	params = line.split(',')
	params[0] = params[0].split('=')[1]
	params[1] = params[1].split('=')[1]
	width = max(int(params[0])+offset[0], min_size[0])
	height = max(int(params[1])+offset[1], min_size[1])
	state = np.zeros((width, height), dtype=np.uint8)
	state_buffer = state[offset[0]:, offset[1]:	]
	x = 0
	y = 0
	buffer = ''
	while True:
		char = read_file.read(1)
		if char == 'b':
			if buffer == '':
				state_buffer[x, y] = 0
				x += 1
			else:
				state_buffer[x:x+int(buffer), y] = 0
				x += int(buffer)
				buffer = ''
		elif char == 'o':
			if buffer == '':
				state_buffer[x, y] = 1
				x += 1
			else:
				state_buffer[x:x+int(buffer), y] = 1
				x += int(buffer)
				buffer = ''
		elif char == '$':
			if buffer == '':
				y += 1
				x = 0
			else:
				y += int(buffer)
				x = 0
				buffer = ''
		elif char == '!':
			break
		elif char.isdigit():
			buffer += char
	read_file.close()
	return state


def load_data(file_name, min_size=(0,0)):
	"""Loads a state from a file"""
	if file_name is None:
		return None
	
	if file_name.endswith('.rle'):
		return rle_decode(file_name, min_size)

	read_file = open(file_name, 'r', encoding='utf-8')
	size_line = read_file.readline()
	size = size_line.split(',')
	width = int(size[0])
	height = int(size[1])
	if min_size is not None:
		width = max(width, min_size[0])
		height = max(height, min_size[1])
	state = np.zeros((width, height), dtype=np.uint8)
	segment_amount = int(read_file.readline())
	for i in range(segment_amount):
		segment_line = read_file.readline()
		segment = segment_line.split(',')
		x = int(segment[0])
		y = int(segment[1])
		segment_width = int(segment[2])
		segment_height = int(segment[3])
		for j in range(segment_height):
			line = read_file.readline()
			line = line.split(',')
			line = [int(x) for x in line]
			state[x:x+segment_width, y+j] = line
	read_file.close()
	print(state.shape)
	return state

def find_bounds(state): 
	x_min = 0
	x_max = state.shape[0]
	y_min = 0
	y_max = state.shape[1]
	for i in range(state.shape[0]):
		if np.any(state[i,:]):
			x_min = i
			break
	for i in range(state.shape[0]-1, -1, -1):
		if np.any(state[i,:]):
			x_max = i
			break
	for i in range(state.shape[1]):
		if np.any(state[:,i]):
			y_min = i
			break
	for i in range(state.shape[1]-1, -1, -1):
		if np.any(state[:,i]):
			y_max = i
			break
	return (x_min, x_max, y_min, y_max)
	

def save_state(file_name, state):
	"""Saves a state to a file in RLE format"""
	if file_name is None:
		return
	bounds = find_bounds(state)
	state = state[bounds[0]:bounds[1]+1, bounds[2]:bounds[3]+1]
	
	write_file = open(file_name, 'w', encoding='utf-8')
	write_file.write(f'#N Game of Life\n')
	write_file.write(f'#C Created by Game of Life\n')
	write_file.write(f'#R 10 10\n')
	write_file.write(f'x={state.shape[0]},y={state.shape[1]},rule=B3/S23\n')
	prev_cell = 0
	count = 0
	for i in range(state.shape[1]):
		for j in range(state.shape[0]):
			if state[j,i] == 1:
				if prev_cell == 0:
					if count > 1:
						write_file.write(str(count))
						write_file.write('b')
					elif count == 1:
						write_file.write('b')
					count = 1
					prev_cell = 1
				else:
					count += 1
			else:
				if prev_cell == 1:
					if count > 1:
						write_file.write(str(count))
						write_file.write('o')
					elif count == 1:
						write_file.write('o')
					count = 1
					prev_cell = 0
				else:
					count += 1
		if count > 1:
			write_file.write(str(count))
			if prev_cell == 1:
				write_file.write('o')
			else:
				write_file.write('b')
		elif count == 1:
			if prev_cell == 1:
				write_file.write('o')
			else:
				write_file.write('b')
		count = 0
		prev_cell = 0
		write_file.write('$')
	write_file.write('!')
	write_file.close()