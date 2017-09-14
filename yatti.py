"""yatti module
Author = Richard D. Fears
Created = 2017-08-25
Description = Main file of the YATTi program. Builds and displays all of the necessary screens
	(e.g. timers, calendar, timer data). Also reads and writes out the theme, data, settings,
	and password files.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import os, sys, json, base64, time
from appdirs import AppDirs
# My code imports
import helper
from timerbutton import TimerButton
from dataeditor import DataEditor

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
		'dataeditor':{},
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
		'timerbuttons':{},
		'root width':1200,
		'root height':800,
		'pause other timers':True,
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
	DATA_CONFIG = [
		{'type':'string','text':"Title/Ticket",'key':'title'},
		{'type':'string','text':"Description",'key':'description'},
		{'type':'string','text':"Source System",'key':'source system'},
		{'type':'table','text':"Intervals",'key':'intervals','columns':[
			{'type':'datetime','text':"Start"},
			{'type':'datetime','text':"End"},
			{'type':'boolean','text':"Exported"},
			{'type':'string','text':"Description"},
		]},
	]
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

	def __init__ (self):
		"""YattiMain constructor
		Reads in the default theme, data, settings, and password files. If any of them do not exist
		yet, it creates base versions.
		"""
		# Get the preferred settings location
		global DEBUG
		try:
			DEBUG
		except:
			DEBUG = False
		if DEBUG:
			self._dirs = AppDirs(appname="YATTi",appauthor="GrayShadowSoftware",version="Debug")
		else:
			self._dirs = AppDirs(appname="YATTi",appauthor="GrayShadowSoftware")
		configprefix = self._dirs.user_config_dir
		dataprefix = self._dirs.user_data_dir
		# First read in the settings file
		self._settingsfilename = "settings.json"
		self._settings = self._load_file_or_defaults("settings",
			configprefix+os.sep+self._settingsfilename,
			self._settings_version_update,self.DEFAULT_SETTINGS)
		# The settings file will contain the rest of the filenames
		self._theme = self._load_file_or_defaults("theme",
			configprefix+os.sep+self._settings['theme file'],
			self._theme_version_update,self.DEFAULT_THEME)
		self._data = self._load_file_or_defaults("data",
			dataprefix+os.sep+self._settings['data file'],
			self._data_version_update,self.DEFAULT_DATA)
		self._passwords = self._load_file_or_defaults("passwords",
			configprefix+os.sep+self._settings['passwords file'],
			self._passwords_version_update,self.DEFAULT_PASSWORDS,self._decrypt_password_file)

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

	def _canvas_reconfigure (self):
		"""_canvas_reconfigure callback function
		Reconfigures the canvas's scrollregion and width when its view is reconfigured.
		"""
		# Only reconfigure the canvas if it's already been rendered
		if not self._canvas.winfo_viewable():
			self._canvas.after(20,self._canvas_reconfigure)
			return
		self._canvas.config(
			scrollregion=self._canvas.bbox('all'),
			width=self._timerframe.winfo_width()
		)

	def run (self):
		"""run function
		Main driver function for YATTi program. Builds all the widgets and runs the main loop.
		"""
		self._root = tk.Tk()
		self._root.title("YATTi - Yet Another Tracker of Time")
		self._root.protocol("WM_DELETE_WINDOW",self._close_window)
		self._root.iconbitmap("YATTi.ico")
		# Grab the previous size from the settings and place the window in the center of the screen
		rootwidth = self._settings['root width']
		rootheight = self._settings['root height']
		screenwidth = self._root.winfo_screenwidth()
		screenheight = self._root.winfo_screenheight()
		xpos = (screenwidth/2)-(rootwidth/2)
		ypos = (screenheight/2)-(rootheight/2)
		self._root.geometry('%dx%d+%d+%d'%(rootwidth,rootheight,xpos,ypos))
		# Right pane column and timer list row should expand when window resized
		self._root.grid_columnconfigure(2,weight=1)
		self._root.grid_rowconfigure(1,weight=1)
		self._timers = []
		### Menu ###
		menubar = tk.Menu(self._root)
		self._root.config(menu=menubar)
		# File menu
		filemenu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File",underline=0,menu=filemenu)
		filemenu.add_command(label="Save",underline=0,command=self._write_all_files)
		# Timer menu
		timermenu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Timers",underline=0,menu=timermenu)
		timermenu.add_command(label="Add New Timer",underline=0,command=self._add_timer)
		### Left pane ###
		# Timer button frame
		timerframeouter = tk.Frame(self._root)
		timerframeouter.grid(column=1,row=1,sticky='ns')
		self._canvas = tk.Canvas(timerframeouter)
		self._timerframe = tk.Frame(self._canvas)
		self._timerframe.pack()
		timerscrollbar = tk.Scrollbar(timerframeouter,orient='vertical',command=self._canvas.yview)
		self._canvas.config(yscrollcommand=timerscrollbar.set)
		timerscrollbar.pack(side='right',fill='y',expand=True)
		self._canvas.pack(side='left',fill='y',expand=True)
		self._canvas.create_window((0,0),window=self._timerframe,anchor='nw')
		self._timerframe.bind('<Configure>',lambda e,self=self: self._canvas_reconfigure)
		# Add quick-add button
		self._button_font = tkfont.Font()
		self._quick_add_button = tk.Button(self._root,font=self._button_font,
			text="Quick-Add Timer",command=self._add_timer)
		self._quick_add_button.grid(column=1,row=2)

		### Right pane ###
		self._current_timerbutton = None
		self._dataeditor_updater = None
		dataeditorframe = tk.Frame(self._root)
		dataeditorframe.grid(row=1,column=2,rowspan=2,sticky='nw')
		self._dataeditor = DataEditor(dataeditorframe,self.DATA_CONFIG,self._theme['dataeditor'])
		self._dataeditor.pack()
		self._dataeditor.register_save_callback(self._data_editor_saved)
		self._dataeditorerrors = tk.Label(dataeditorframe,text=" ")
		self._dataeditorerrors.pack()

		### Adding timer buttons and reconfiguring ###
		self._load_timers_from_json()
		self.update_theme()

		self._root.mainloop()

	def _close_window (self):
		"""_close_window internal function
		Callback for when the main window is closed. Saves all files and then exits.
		"""
		self._write_all_files()
		self._root.destroy()

	def _set_current_timerbutton (self, tb):
		"""_set_current_timerbutton internal function
		Called when clicking on a timer label. Initializes the data editor's data.
		"""
		self._current_timerbutton = tb
		self._dataeditor.load_data(self._current_timerbutton._data)
		self._dataeditor.enable(tables=not self._current_timerbutton.running)

		if self._dataeditor_updater != None:
			self._root.after_cancel(self._dataeditor_updater)
			self._dataeditor_updater = None
		if self._current_timerbutton.running:
			self._dataeditor_updater = self._root.after(500,self._update_dataeditor)

	def _update_dataeditor (self):
		"""_update_dataeditor internal function
		Updates the intervals section of the data editor, allowing a running timer.
		"""
		self._dataeditor.update_data_for_key('intervals')
		self._dataeditor_updater = self._root.after(500,self._update_dataeditor)

	def _data_editor_saved (self, errors):
		"""_data_editor_saved internal function
		Called when the data editor save button is clicked. Updates the timer button data.
		"""
		if self._current_timerbutton == None:
			return
		self._current_timerbutton.update_data()
		if len(errors) > 0:
			self._dataeditorerrors.configure(fg='red',text=str(len(errors))+" errors while saving")
		else:
			self._dataeditorerrors.configure(fg='dark green',text="Saved successfully")

	def _write_all_files (self):
		"""_write_all_files internal function
		Writes the settings, theme, data, and passwords dictionaries to their respective files.
		"""
		self._write_file("settings",self._settings,self._dirs.user_config_dir,
			self._settingsfilename)
		self._write_file("theme",self._theme,self._dirs.user_config_dir,
			self._settings['theme file'])
		self._write_file("data",self._data,self._dirs.user_data_dir,
			self._settings['data file'])
		self._write_file("passwords",self._passwords,self._dirs.user_config_dir,
			self._settings['passwords file'],self._encrypt_password_file)

	def _write_file (self, dictname, sourcedict, filedir, filename, wrapperfunc = None):
		"""_write_file internal function
		Writes the given sourcedict as JSON to the given filename, optionally running wrapperfunc
		on the JSON first.
		"""
		# Create the directory
		if not os.path.exists(filedir):
			os.makedirs(filedir)
		# Try to write out the JSON
		try:
			with open(filedir+os.sep+filename,'w') as fileobj:
				if wrapperfunc == None:
					json.dump(sourcedict,fileobj,indent="\t",separators=(', ',':'))
				else:
					fileobj.write(wrapperfunc(json.dumps(sourcedict,"\t",separators=(', ',':'))))
			return True
		# If we can't, notify the user
		except:
			print(dictname+" JSON could not be written to "+(filedir+os.sep+filename)+".",
				file=sys.stderr)
			traceback.print_exc()
			return False

	def _load_timers_from_json (self):
		"""_load_timers_from_json internal function
		Adds all the timers found in the JSON file that was read in at the start of the program.
		"""
		for data in self._data['timerdata']:
			self._add_timer(data)

	def _add_timer (self, timerdata=None):
		"""_add_timer internal function
		Adds a timer button to the list. timerdata can be specified if loading an existing timer.
		"""
		if timerdata == None:
			self._data['timerdata'].append({})
			timerdata = self._data['timerdata'][-1]
		self._timers.append(TimerButton(self._timerframe,timerdata,self._settings['timerbuttons'],
			self._theme['timerbuttons']))
		self._timers[-1].pack()
		self._timers[-1].update_theme()
		self._timers[-1].register_toggle_callback(self._timer_toggled)
		self._timers[-1].register_labelclick_callback(self._set_current_timerbutton)
		self._canvas_reconfigure()
		self._canvas.yview_moveto(1)

	def _timer_toggled (self, thetimer):
		"""_timer_toggled callback function
		The function which is called for each timer when said timer is toggled.
		"""
		# If we want to pause other timers when this one is started, do so
		if self._settings['pause other timers'] and thetimer.running:
			for timer in self._timers:
				if timer != thetimer:
					timer.turn_off()
		# If there is a running dataeditor updater, cancel it before checking if we should start
		# a new one
		if self._dataeditor_updater != None:
			self._root.after_cancel(self._dataeditor_updater)
			self._dataeditor_updater = None
		if thetimer == self._current_timerbutton:
			self._dataeditor.enable(tables=not self._current_timerbutton.running)
			if self._current_timerbutton.running:
				self._dataeditor_updater = self._root.after(500,self._update_dataeditor)

	def update_theme (self):
		"""update_theme function
		Updates the fonts/colors/styles from the theme attribute. Used when the user changes
		the theme.
		"""
		widgets = (
			(self._quick_add_button,'basic'),
			(self._root,'widget'),
			(self._quick_add_button,'buttons'),
		)
		fontwidgets = (
			(self._button_font,'buttons'),
		)
		subwidgets = [self._dataeditor]+self._timers

		for widget,name in widgets:
			helper.configThemeFromDict(widget,self._theme,'base',name)
		for widget,name in fontwidgets:
			helper.configThemeFromDict(widget,self._theme,'fonts',name)
		for widget in subwidgets:
			widget.update_theme()


if __name__ == "__main__":
	import os, sys, traceback
	# cd to the script directory
	try:
		if getattr(sys,'frozen',False):
			# The app is frozen, so get the dir of the executable
			os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
		else:
			# The app is not frozen, so we should use the location of the script file
			os.chdir(os.path.dirname(os.path.abspath(__file__)))
	except Exception as e:
		print("No execute access to script directory")
		raise
	# Check if we were passed the debug flag
	if len(sys.argv) > 1 and sys.argv[1] == "--debug":
		DEBUG = True
	else:
		DEBUG = False

	try:
		main = YattiMain()
		main.run()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		# If the app is not frozen, pause the console window so we can see errors
		if not getattr(sys,'frozen',False):
			input("Press enter to quit")

