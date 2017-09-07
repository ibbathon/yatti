"""yatti module
Author = Richard D. Fears
Created = 2017-08-25
LastModified = 2017-09-07
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
	OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
	DEFAULT_THEME = {
		'version':[1,0,0],
		'calendar':{},
		'timerbuttons':{},
		'base':{
			'buttons':{},
		},
		'fonts':{
			'buttons':{'size':20,},
		},
	}
	OLDEST_CONVERTIBLE_SETTINGS_VERSION = [1,0,0]
	DEFAULT_SETTINGS = {
		'version':[1,0,0],
		'root width':1200,
		'root height':800,
		'theme file':'default-theme.json',
		'data file':'timerdata.json',
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
	OLDEST_CONVERTIBLE_DATA_VERSION = [1,0,0]
	DEFAULT_DATA = {
		'version':[1,0,0],
		'timerdata':[],
	}
	OLDEST_CONVERTIBLE_PASSWORDS_VERSION = [1,0,0]
	DEFAULT_PASSWORDS = {
		'version':[1,0,0],
		'jira':'',
		'openair':'',
		'trac':'',
	}

	def _settings_version_update (self, oldsettings):
		"""_settings_version_update internal function
		Updates the old settings to the new format, based on relative versions.
		"""
		# Check for versions which are incompatible with list-of-numbers versions
		try:
			oldsettings['version'] < [0]
		except:
			raise VersionException(VersionException.BAD_TYPE,oldsettings['version'])

		# If the settings version is later than the program version, we will not know how to convert
		if oldsettings['version'] > YattiMain.DEFAULT_SETTINGS['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldsettings['version'],YattiMain.DEFAULT_SETTINGS['version'])

		# If the old version is too old, we will not know how to convert
		if oldsettings['version'] < YattiMain.OLDEST_CONVERTIBLE_SETTINGS_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldsettings['version'],YattiMain.DEFAULT_SETTINGS['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if oldsettings['version'] < [1,1]:
		#	oldsettings['somevariable'] = oldsettings['oldvariable']
		#	oldsettings['version'] = [1,1]

	def _theme_version_update (self, oldtheme):
		"""_theme_version_update internal function
		Updates the old theme to the new format, based on relative versions.
		"""
		# Check for versions which are incompatible with list-of-numbers versions
		try:
			oldtheme['version'] < [0]
		except:
			raise VersionException(VersionException.BAD_TYPE,oldtheme['version'])

		# If the theme version is later than the program version, we will not know how to convert
		if oldtheme['version'] > YattiMain.DEFAULT_THEME['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldtheme['version'],YattiMain.DEFAULT_THEME['version'])

		# If the old version is too old, we will not know how to convert
		if oldtheme['version'] < YattiMain.OLDEST_CONVERTIBLE_THEME_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldtheme['version'],YattiMain.DEFAULT_THEME['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if oldtheme['version'] < [1,1]:
		#	oldtheme['somevariable'] = oldtheme['oldvariable']
		#	oldtheme['version'] = [1,1]

	def _passwords_version_update (self, oldpasswords):
		"""_passwords_version_update internal function
		Updates the old passwords to the new format, based on relative versions.
		"""
		# Check for versions which are incompatible with list-of-numbers versions
		try:
			oldpasswords['version'] < [0]
		except:
			raise VersionException(VersionException.BAD_TYPE,oldpasswords['version'])

		# If the passwords version is later than the program version,
		# we will not know how to convert
		if oldpasswords['version'] > YattiMain.DEFAULT_PASSWORDS['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldpasswords['version'],YattiMain.DEFAULT_PASSWORDS['version'])

		# If the old version is too old, we will not know how to convert
		if oldpasswords['version'] < YattiMain.OLDEST_CONVERTIBLE_PASSWORDS_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldpasswords['version'],YattiMain.DEFAULT_PASSWORDS['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if oldpasswords['version'] < [1,1]:
		#	oldpasswords['somevariable'] = oldpasswords['oldvariable']
		#	oldpasswords['version'] = [1,1]

	def _data_version_update (self, olddata):
		"""_data_version_update internal function
		Updates the old data to the new format, based on relative versions.
		"""
		# Check for versions which are incompatible with list-of-numbers versions
		try:
			olddata['version'] < [0]
		except:
			raise VersionException(VersionException.BAD_TYPE,olddata['version'])

		# If the data version is later than the program version, we will not know how to convert
		if olddata['version'] > YattiMain.DEFAULT_DATA['version']:
			raise VersionException(VersionException.TOO_NEW,
				olddata['version'],YattiMain.DEFAULT_DATA['version'])

		# If the old version is too old, we will not know how to convert
		if olddata['version'] < YattiMain.OLDEST_CONVERTIBLE_DATA_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				olddata['version'],YattiMain.DEFAULT_DATA['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if olddata['version'] < [1,1]:
		#	olddata['somevariable'] = olddata['oldvariable']
		#	olddata['version'] = [1,1]

	def _decrypt_password_file (self, filetext):
		"""_decrypt_password_file internal function
		Takes raw text from an encrypted file and converts it to decrypted JSON text string.
		TODO: Currently just returns the filetext. Need to actually add decryption logic.
		"""
		return filetext

	def _encrypt_password_file (self, jsontext):
		"""_encrypt_password_file internal function
		Takes a JSON text string and converts it to an encrypted string for writing to a file.
		TODO: Currently just returns the jsontext. Need to actually add encryption logic.
		"""
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
		self._settingsfilename = "settings.json"
		self._settings = self._load_file_or_defaults("settings",self._settingsfilename,
			self._settings_version_update,self.DEFAULT_SETTINGS)
		# The settings file will contain the rest of the filenames
		self._theme = self._load_file_or_defaults("theme",self._settings['theme file'],
			self._theme_version_update,self.DEFAULT_THEME)
		self._data = self._load_file_or_defaults("data",self._settings['data file'],
			self._data_version_update,self.DEFAULT_DATA)
		self._passwords = self._load_file_or_defaults("passwords",self._settings['passwords file'],
			self._passwords_version_update,self.DEFAULT_PASSWORDS,self._decrypt_password_file)

	def _canvas_reconfigure (self):
		"""_canvas_reconfigure callback function
		Reconfigures the canvas's scrollregion and width when its view is reconfigured.
		"""
		# Only reconfigure the canvas if it's already been rendered
		if not self._canvas.winfo_viewable():
			self._canvas.after(20,self._canvas_reconfigure)
			return
		self._canvas.configure(
			scrollregion=self._canvas.bbox('all'),
			width=self._timerframe.winfo_width()
		)

	def run (self):
		"""run function
		Main driver function for YATTi program. Builds all the widgets and runs the main loop.
		"""
		self._root = tk.Tk()
		# Grab the previous size from the settings and place the window in the center of the screen
		rootwidth = self._settings['root width']
		rootheight = self._settings['root height']
		screenwidth = self._root.winfo_screenwidth()
		screenheight = self._root.winfo_screenheight()
		xpos = (screenwidth/2)-(rootwidth/2)
		ypos = (screenheight/2)-(rootheight/2)
		self._root.geometry('%dx%d+%d+%d'%(rootwidth,rootheight,xpos,ypos))
		# Column 3 (right pane) and row 2 (timer list) should expand when window resized
		self._root.grid_columnconfigure(3,weight=1)
		self._root.grid_rowconfigure(2,weight=1)
		self._timers = []
		### Left pane ###
		# Calendar
		self._cal = Calendar(self._root,self._theme['calendar'])
		self._cal.grid(column=1,row=1)
		# Add buttons
		buttonframe = tk.Frame(self._root)
		buttonframe.grid(column=2,row=1)
		self._button_font = tkfont.Font()
		self._add_button = tk.Button(buttonframe,font=self._button_font,text="Add Timer")
		self._add_button.pack()
		self._quick_add_button = tk.Button(buttonframe,font=self._button_font,
			text="Quick-Add Timer")
		self._quick_add_button.pack()
		# Timer button frame
		timerframeouter = tk.Frame(self._root)
		timerframeouter.grid(column=1,row=2,columnspan=2,sticky='ns')
		self._canvas = tk.Canvas(timerframeouter)
		self._timerframe = tk.Frame(self._canvas)
		self._timerframe.pack()
		timerscrollbar = tk.Scrollbar(timerframeouter,orient='vertical',command=self._canvas.yview)
		self._canvas.configure(yscrollcommand=timerscrollbar.set)
		timerscrollbar.pack(side='right',fill='y',expand=True)
		self._canvas.pack(side='left',fill='y',expand=True)
		self._canvas.create_window((0,0),window=self._timerframe,anchor='nw')
		self._timerframe.bind('<Configure>',lambda e,self=self: self._canvas_reconfigure)

		### Right pane ###
		templabel = tk.Label(self._root,text="Blah")
		templabel.grid(row=1,column=3,rowspan=2)
		#templabel.bind('<Button-1>', lambda e,canvas=self._canvas: canvas.yview_moveto(1))

		### Adding timer buttons and reconfiguring ###
		self._timerframe.after(5,self.debugadd)
		self.update_theme()

		self._root.mainloop()

	def update_theme (self):
		"""update_theme function
		Updates the fonts/colors/styles from the theme attribute. Used when the user changes
		the theme.
		"""
		widgets = (
			(self._add_button,'basic'),
			(self._quick_add_button,'basic'),
			(self._root,'widget'),
			(self._add_button,'buttons'),
			(self._quick_add_button,'buttons'),
		)
		fontwidgets = (
			(self._button_font,'buttons'),
		)
		subwidgets = [self._cal]+self._timers

		for widget,name in widgets:
			helper.configThemeFromDict(widget,self._theme,'base',name)
		for widget,name in fontwidgets:
			helper.configThemeFromDict(widget,self._theme,'fonts',name)
		for widget in subwidgets:
			widget.update_theme()


	def debugadd (self):
		if not self._timerframe.winfo_viewable():
			self._timerframe.after(5,self.debugadd)
			return
		for i in range(10):
			self._timers.append(TimerButton(self._timerframe,
				timertheme=self._theme['timerbuttons']))
		for i in range(10):
			self._timers[i].pack()
		self._timerframe.update()
		self._canvas_reconfigure()


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

