"""setup module
Author = Richard D. Fears
Created = 2017-09-14
Description = Compiles the YATTi driver program into an exe.
"""

import os,sys
from cx_Freeze import setup, Executable

os.environ['TCL_LIBRARY'] = "C:/Program Files (x86)/Python35-32/tcl/tcl8.6"
os.environ['TK_LIBRARY'] = "C:/Program Files (x86)/Python35-32/tcl/tk8.6"

build_exe_options = {
	'include_files':[
		"C:/Program Files (x86)/Python35-32/DLLs/tcl86t.dll",
		"C:/Program Files (x86)/Python35-32/DLLs/tk86t.dll"
	]
}

base = None
if sys.platform == "win32":
	base = "Win32GUI"

setup(
	name = "YATTi",
	version = "0.1",
	description = "YATTi - Yet Another Tracker of Time",
	options = {'build_exe':build_exe_options},
	executables = [Executable("yatti.py", base=base)]
)
