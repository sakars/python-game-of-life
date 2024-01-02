"""This file is used to compile the C code into a binary file that can be imported into python."""
import os
import sysconfig
import glob
from setuptools import Extension, setup
import numpy as np
# Glob pattern for the C source files
path = r'./GOL/core/src/*.c'
files = glob.glob(path)

python_include_dir = sysconfig.get_paths()["include"]
file_path = os.path.abspath(__file__)
folder_path = os.path.dirname(file_path)
GOLCore_include_path = os.path.join(folder_path, "GOL/core/include")

setup(
	packages=["GOL"],
	ext_modules=[
		Extension(
			name="GOL.core",  # as it would be imported
			include_dirs=[
				python_include_dir,
				GOLCore_include_path,
				np.get_include()
			],
			sources=files,  # all sources are compiled into a single binary file
		)
	],
	name="GOL"
)