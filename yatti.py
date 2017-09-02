"""yatti module
Author = Richard D. Fears
Created = 2017-08-25
LastModified = 2017-08-25
Description = Main file of the YATTi program. Builds and displays all of the necessary screens
	(e.g. timers, calendar, timer data). Also reads and writes out the theme, data, settings,
	and password files.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import sys, json, base64, time
# My code imports
import helper
from calendarwidget import Calendar
from timerbutton import TimerButton

class YattiMain:
	"""YattiMain class
	Driver class for the YATTi program.
	"""

	# DO NOT CHANGE THE DEFAULTS BELOW!
	# If you want to change your personal theme, edit 'default-theme.json' instead.
	# If you want to change your settings, edit settings.json.
	DEFAULT_THEME = {
		'version':[1,0,0],
		'calendar':{},
		'timerbuttons':{},
	}
	DEFAULT_SETTINGS = {
		'version':[1,0,0],
		'theme file':'default-theme.json',
		'passwords file':'passwords.bin',
		'connection info':{
			'jira':{
				'site':'',
				'username':'',
				'save password':'',
			},
			'openair':{
				'site':'',
				'username':'',
				'save password':'',
			},
			'trac':{
				'site':'',
				'username':'',
				'save password':'',
			},
		},
	}
	DEFAULT_DATA = {
		'version':[1,0,0],
		'timerdata':[],
	}
	DEFAULT_PASSWORDS = {
		'version':[1,0,0],
		'jira':'',
		'openair':'',
		'trac':'',
	}

	def _settings_version_update (self, oldsettings):
		pass

	def _theme_version_update (self, oldtheme):
		pass

	def _passwords_version_update (self, oldpasswords):
		pass

	def _data_version_update (self, olddata):
		pass

	def _decrypt_password_file (self, filetext):
		return filetext

	def _encrypt_password_file (self, jsontext):
		return jsontext

	def _load_file_or_defaults (self, dictname, filename, updatefunc, defaults, wrapperfunc = None):
		"""_load_file_or_defaults internal function
		Reads JSON from a file if it exists. If it doesn't, loads from defaults.
		In either case, it returns the resulting dict.
		"""
		# Try to read in the JSON file
		try:
			with open(filename) as fileobj:
				if wrapperfunc == None:
					thedict = json.load(fileobj)
				else:
					thedict = json.loads(wrapperfunc(fileobj.read()))
		# If we can't, default to a basic dict
		except:
			print("No "+filename+" file found. Creating default "+dictname+".",file=sys.stderr)
			thedict = {}
		# We've either read in and interpreted a JSON dict, or created a base one.
		# Now make sure to update it/fill it with defaults.
		thedict = helper.dictVersionUpdate(thedict,updatefunc,defaults)
		return thedict

	def __init__ (self):
		"""YattiMain constructor
		Reads in the default theme, data, settings, and password files. If any of them do not exist
		yet, it creates base versions.
		"""
		# First read in the settings file
		settingsfilename = "settings.json"
		self._settings = self._load_file_or_defaults("settings",settingsfilename,
			self._settings_version_update,self.DEFAULT_SETTINGS)
		# The settings file will contain the rest of the filenames
		self._theme = self._load_file_or_defaults("theme",self._settings['theme file'],
			self._theme_version_update,self.DEFAULT_THEME)
		self._passwords = self._load_file_or_defaults("passwords",self._settings['passwords file'],
			self._passwords_version_update,self.DEFAULT_PASSWORDS,self._decrypt_password_file)
		# Build the filename for today's data and try to load it
		todaysts = time.strftime('%Y%m%d')
		todaysdatafilename = todaysts+'.json'
		self._data = self._load_file_or_defaults("data",todaysdatafilename,
			self._data_version_update,self.DEFAULT_DATA)

	def run (self):
		"""run function
		Main driver function for YATTi program. Builds all the widgets and runs the main loop.
		"""
		root = tk.Tk()
		root.grid_columnconfigure(1,weight=1,minsize=200)
		root.grid_columnconfigure(2,weight=3,minsize=400)
		root.grid_rowconfigure(2,weight=1)
		self._timers = []
		### Left pane ###
		# Calendar
		cal = Calendar(root,self._theme['calendar'])
		cal.grid(column=1,row=1)
		# Timer button frame
		timerframeouter = tk.Frame(root)
		timerframeouter.pack_propagate(False)
		timerframeouter.grid(column=1,row=2,sticky='nsew')
		canvas = tk.Canvas(timerframeouter)
		self._timerframe = tk.Frame(canvas)
		self._timerframe.pack_propagate(False)
		self._timerframe.pack(fill='both',expand=True)
		timerscrollbar = tk.Scrollbar(timerframeouter,orient='vertical',command=canvas.yview)
		canvas.configure(yscrollcommand=timerscrollbar.set)
		timerscrollbar.pack(side='right',fill='y')
		canvas.pack(side='left',fill='both',expand=True)
		canvas.create_window((0,0),window=self._timerframe,anchor='nw')
		self._timerframe.bind('<Configure>',lambda e, canvas=canvas, \
			timerframeouter=timerframeouter, timerscrollbar=timerscrollbar: \
			canvas.configure(scrollregion=canvas.bbox('all'), \
			width=timerframeouter.winfo_width()-timerscrollbar.winfo_width(),
			height=timerframeouter.winfo_height()))
		#self._timerframe.bind('<Configure>',lambda e, canvas=canvas: canvas.pack(side='left',fill='both',expand=True))

		for i in range(10):
			self._timers.append(TimerButton(self._timerframe,
				timertheme=self._theme['timerbuttons']))
			self._timers[-1].pack()
		#self._theme['timerbuttons']['base']['widget']['width'] = 100
		#for i in range(10):
		#	self._timers[i].update_theme()
		#self._timerframe.pack_propagate(False)
		#self._timerframe.configure(width=100,height=100)

		tk.Label(root,text="Blah").grid(row=1,column=2,rowspan=3)

		root.mainloop()


if __name__ == "__main__":
	import os, traceback
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	try:
		main = YattiMain()
		main.run()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")

