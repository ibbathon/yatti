"""timerbutton module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-31
Description = Provides the TimerButton Tk widget, which contains a timer label, timer description,
	and button to start/stop the timer.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import time
# My code imports
import helper
from versionexception import VersionException

class TimerButton (tk.Frame):
	"""TimerButton class
	Displays a grid Frame with a description label on the far left, count-up timer in the middle,
	and a button to start/stop the timer on the far right.
	"""

	OLDEST_CONVERTIBLE_DATA_VERSION = [1,0,0]
	DEFAULT_DATA = {
		'version':[1,0,0],
		'intervals':[],
		'title':"TIMER",
		'description':"Default timer"
	}
	OLDEST_CONVERTIBLE_SETTINGS_VERSION = [1,0,0]
	DEFAULT_SETTINGS = {
		'version':[1,0,0],
		'merge qualifications':{
			'overlapping intervals':True,
			'adjacent intervals':True,
			'delete short':True,
			'max adjacency distance':2.0,
			'max short distance':2.0,
		}
	}
	OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
	DEFAULT_THEME = {
		'version':[1,0,0],
		'base':{
			'widget':{'bd':2,'relief':'raised','width':200,},
			'title':{'fg':'black',},
			'desc':{'fg':'black',},
			'time':{'fg':'black',},
			'start':{'fg':'green','width':4,'height':2,},
		},
		'active':{
			'widget':{'relief':'sunken',},
			'title':{'fg':'dark green',},
			'desc':{'fg':'dark green',},
			'time':{'fg':'dark green',},
			'start':{'fg':'red',},
		},
		'fonts':{
			'title':{'size':20,},
			'desc':{'size':12,},
			'time':{'size':24,},
			'start':{'size':12,}
		},
	}

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
		if olddata['version'] > TimerButton.DEFAULT_DATA['version']:
			raise VersionException(VersionException.TOO_NEW,
				olddata['version'],TimerButton.DEFAULT_DATA['version'])

		# If the old version is too old, we will not know how to convert
		if olddata['version'] < TimerButton.OLDEST_CONVERTIBLE_DATA_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				olddata['version'],TimerButton.DEFAULT_DATA['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if olddata['version'] < [1,1]:
		#	olddata['somevariable'] = olddata['oldvariable']
		#	olddata['version'] = [1,1]

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
		if oldsettings['version'] > TimerButton.DEFAULT_SETTINGS['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldsettings['version'],TimerButton.DEFAULT_SETTINGS['version'])

		# If the old version is too old, we will not know how to convert
		if oldsettings['version'] < TimerButton.OLDEST_CONVERTIBLE_SETTINGS_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldsettings['version'],TimerButton.DEFAULT_SETTINGS['version'])

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
		if oldtheme['version'] > TimerButton.DEFAULT_THEME['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldtheme['version'],TimerButton.DEFAULT_THEME['version'])

		# If the old version is too old, we will not know how to convert
		if oldtheme['version'] < TimerButton.OLDEST_CONVERTIBLE_THEME_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldtheme['version'],TimerButton.DEFAULT_THEME['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if oldtheme['version'] < [1,1]:
		#	oldtheme['somevariable'] = oldtheme['oldvariable']
		#	oldtheme['version'] = [1,1]

	def __init__ (self, parent, timerdata=None, timersettings=None, timertheme=None,
		*args, **options):
		"""TimerButton constructor
		timerdata, timersettings, and timertheme are pre-populated versions of each of the defaults
		defined within this class, for initializing a timer button with non-default
		data/settings/theme.
		title is the very-short description of the timer (<15 chars).
		description is a longer description and will be truncated appropriately.
		"""
		super().__init__(parent,*args,**options)

		# Initialize internal variables
		# The callbacks array for when the toggle function is called
		self._toggle_callbacks = []
		# The callbacks array for when any other part of the widget is clicked
		self._labelclick_callbacks = []

		# Update the timerdata, timersettings, and timertheme parameters (or set to defaults)
		self._data = helper.dictVersionUpdate(timerdata,self._data_version_update,
			self.DEFAULT_DATA)
		self._settings = helper.dictVersionUpdate(timersettings,self._settings_version_update,
			self.DEFAULT_SETTINGS)
		self._theme = helper.dictVersionUpdate(timertheme,self._theme_version_update,
			self.DEFAULT_THEME)

		# Build the title and description labels
		tk.Grid.columnconfigure(self,1,weight=1)
		self._title_font = tkfont.Font()
		self._title_label = tk.Label(self,font=self._title_font,anchor='w')
		self._title_label.grid(column=1,row=1,sticky='we')
		self._desc_font = tkfont.Font()
		self._desc_label = tk.Label(self,font=self._desc_font,anchor='w')
		self._desc_label.grid(column=1,row=2,sticky='we')

		# Build the timer label
		self._running = tk.BooleanVar(False)
		self._timer_updater = None
		self._curr_start_time = None
		self._timer_font = tkfont.Font()
		self._timer_label = tk.Label(self,text="00:00:00",font=self._timer_font)
		self._timer_label.grid(column=2,row=1,rowspan=2,padx=10)
		self._update_timer(restarttimer=False)

		# Build the start/pause button
		self._start_font = tkfont.Font()
		self._start_button = tk.Checkbutton(self,text=helper.PLAY_CHAR,
			command=self._toggle,font=self._start_font,variable=self._running,indicatoron=False)
		self._start_button.grid(column=3,row=1,rowspan=2)

		# Update the theme from the dicts
		self.update_data()
		self.update_theme()

	def _toggle (self):
		"""_toggle internal function
		Toggles the timer between running and paused.
		"""
		if self.running:
			self._start_button.configure(text=helper.PAUSE_CHAR)
			self._curr_start_time = time.time()
			self._timer_updater = self.after(500,self._update_timer)
		else:
			self._start_button.configure(text=helper.PLAY_CHAR)
			self.after_cancel(self._timer_updater)
			self._update_timer(restarttimer=False)
			self._curr_start_time = None
		# Update the font colors
		self._update_active_theme()
		# Call the toggle callback functions
		for f in self._toggle_callbacks:
			f(self)
	
	def turn_off (self):
		"""turn_off function
		Turns off the timer if it's running. Does nothing if it's not.
		Primarily used to turn off all other running timers when starting a new one.
		"""
		if self.running:
			self.running = False
			self._toggle()

	def _update_timer (self, restarttimer=True):
		"""_update_timer internal function
		Updates the label to the new time, as determined by the sum of the intervals in
		timer_data.intervals and the time between curr_start_time and time.time.
		If restarttimer is True, it fires an after with a 500ms delay to call this function.
		"""
		# Grab the current time to compare to the start time
		end_time = time.time()
		# Store the interval
		self._store_time(end_time)
		# We've stored the most recent interval, so check if it should actually exist.
		# If the timer is now off, and we want to delete short (i.e. mistake) intervals,
		# and the most recent interval is short enough, then delete it.
		deleteshort = self._settings['merge qualifications']['delete short']
		shortdistance = self._settings['merge qualifications']['max short distance']
		if (not restarttimer) and deleteshort and self._curr_start_time != None \
			and end_time-self._curr_start_time <= shortdistance:
			del self._data['intervals'][-1]
		# Add up all the time from both the stored intervals and the current interval
		sum_time = self.total_elapsed_time(end_time)
		# Convert it to a readable time and store it in the label
		hours = int(sum_time/3600)
		minutes = int(sum_time/60)%60
		seconds = int(sum_time)%60
		new_text = '{:0>2}:{:0>2}:{:0>2}'.format(hours,minutes,seconds)
		self._timer_label.configure(text=new_text)
		# Setup the next timer
		if restarttimer:
			self._timer_updater = self.after(500,self._update_timer)

	def total_elapsed_time (self, end_time = 0):
		"""total_elapsed_time function
		Add up all the time from both the stored intervals and the current interval.
		"""
		sum_time = 0
		for interval in self._data['intervals']:
			sum_time += interval[1]-interval[0]
		return sum_time

	def _store_time (self,end_time):
		"""_store_time internal function
		Either updates the current/last interval, or adds a new interval. The exact behavior is
		dependent on settings. It can be configured to replace overlapping intervals with
		unioned intervals, replace two nearby intervals with a single joined interval, or always
		store a new interval unless the previous start time exactly matches the current start time.
		"""
		# If the timer is not started right now, there's nothing to store
		if self._curr_start_time == None:
			return
		# If there is no previous interval, skip all the later logic and just add the new interval
		if len(self._data['intervals']) == 0:
			self._data['intervals'].append((self._curr_start_time,end_time))
			return
		# Next, check if the start times match exactly; if they do, skip the later logic
		# and just replace the latest interval
		if self._data['intervals'][-1][0] == self._curr_start_time:
			self._data['intervals'][-1] = (self._curr_start_time,end_time)
			return
		# Now on to the main meat of this function

		# Some helper variables
		replace = False
		replaceOverlapping = self._settings['merge qualifications']['overlapping intervals']
		replaceAdjacent = self._settings['merge qualifications']['adjacent intervals']
		maxAdjacent = self._settings['merge qualifications']['max adjacency distance']
		new_start_time = self._curr_start_time
		new_end_time = end_time
		old_start_time = self._data['intervals'][-1][0]
		old_end_time = self._data['intervals'][-1][1]

		# Check for overlapping intervals
		if replaceOverlapping and new_start_time > old_start_time and new_start_time < old_end_time:
			# The old interval contains the new start time, so we should use the old start time
			replace = True
			new_start_time = old_start_time
		if replaceOverlapping and new_end_time > old_start_time and new_end_time < old_end_time:
			# The old interval contains the new end time, so we should use the old end time
			replace = True
			new_end_time = old_end_time
		# By definition, the overlapping and adjacent conditions cannot happen at the same time,
		# so if there is an overlap replacement, do it now and exit
		if replace:
			self._data['intervals'][-1] = (new_start_time,new_end_time)
			return

		# Check for adjacent intervals
		if replaceAdjacent and new_start_time > old_end_time \
			and new_start_time-old_end_time <= maxAdjacent:
			# The intervals are close enough, so join them
			replace = True
			new_start_time = old_start_time
		if replace:
			self._data['intervals'][-1] = (new_start_time,new_end_time)
			return

		# Finally, we've passed all the logic for joining intervals, we should instead create new
		self._data['intervals'].append((new_start_time,new_end_time))

	def update_data (self):
		"""update_data function
		Updates the labels from the data attribute. Used when the user updates the title/desc.
		"""
		self._title_label.configure(text=self._data['title'])
		self._desc_label.configure(text=self._data['description'])

	def update_theme (self):
		"""update_theme function
		Updates the fonts from the theme attribute. Used when the user changes the theme.
		"""
		widgets = {'widget':self,'title':self._title_label,'desc':self._desc_label,
			'time':self._timer_label,'start':self._start_button}
		fontwidgets = {'title':self._title_font,'desc':self._desc_font,
			'time':self._timer_font,'start':self._start_font}
		for name,widget in widgets.items():
			helper.configThemeFromDict(widget,self._theme,'base',name)
		for name,widget in fontwidgets.items():
			helper.configThemeFromDict(widget,self._theme,'fonts',name)
		self._update_active_theme()

	def _update_active_theme (self):
		"""_update_active_theme internal function
		Updates the colors to active or inactive, based on the state of the timer.
		"""
		widgets = {'widget':self,'title':self._title_label,'desc':self._desc_label,
			'time':self._timer_label,'start':self._start_button}
		if self.running:
			for name,widget in widgets.items():
				helper.configThemeFromDict(widget,self._theme,'active',name)
		else:
			for name,widget in widgets.items():
				helper.configThemeFromDict(widget,self._theme,'base',name)

	def register_toggle_callback (self, callback):
		"""register_toggle_callback function
		Registers a callback function which accepts one argument: this timer button widget.
		The callback function is called when the timer button toggles between active and inactive.
		This allows the main program to detect when the timer button is clicked, which in turn
		allows the main program to disable all other timers.
		"""
		self._toggle_callbacks.append(callback)

	def register_labelclick_callback (self, callback):
		"""register_labelclick_callback function
		Registers a callback function which accepts one argument: this timer button widget.
		The callback function is called when any part of the TimerButton is clicked other than
		the start/pause button itself. This allows the main program to "select" the timer,
		which means it knows when to display the full data.
		"""
		self._labelclick_callbacks.append(callback)
		self._title_label.bind('<Button-1>', lambda e,self=self: callback(self))
		self._desc_label.bind('<Button-1>', lambda e,self=self: callback(self))
		self._timer_label.bind('<Button-1>', lambda e,self=self: callback(self))
		self.bind('<Button-1>', lambda e,self=self: callback(self))

	@property
	def running (self):
		return bool(self._running.get())
	@running.setter
	def running (self, value):
		self._running.set(value)


if __name__ == "__main__":
	import traceback
	try:
		def on_close ():
			for timer in timers:
				timer.turn_off()
			root.destroy()
		def togglecallback (atimer):
			if atimer.running:
				for timer in timers:
					if timer != atimer:
						timer.turn_off()
		def labelcallback (atimer):
			for interval in atimer._data['intervals']:
				print(time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(interval[0])),'-',
					time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(interval[1])))
			print()
		root = tk.Tk()
		timers = []
		timer_datas = [
			{'intervals':[(0,3500)],'title':"COE-4840",
				'description':"A really long, verbose, complicated pile of junk"},
			{'title':"Other timer",'description':"Some short text"},
			{'title':"Yet another timer",'description':"Words"}
		]
		frame = tk.Frame(root,width=400,height=200)
		frame.pack_propagate(False)
		frame.pack(fill='both',expand=True)
		for data in timer_datas:
			timer = TimerButton(frame, timerdata=data)
			timer.pack(fill='x', expand=True)
			timer.register_toggle_callback(togglecallback)
			timer.register_labelclick_callback(labelcallback)
			timers.append(timer)
		root.protocol('WM_DELETE_WINDOW',on_close)
		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")
