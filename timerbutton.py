"""timerbutton module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-22
Description = Provides the TimerButton Tk widget, which contains a timer label, timer description,
	and button to start/stop the timer.
"""
import tkinter as tk
import tkinter.font as tkfont
import time
import helper

class TimerButton (tk.Frame):
	"""TimerButton class
	Displays a grid Frame with a description label on the far left, count-up timer in the middle,
	and a button to start/stop the timer on the far right.
	"""

	DEFAULT_DATA = {
		'intervals':[],
		'title':"TIMER",
		'description':"Default timer"
	}
	DEFAULT_SETTINGS = {
		'fonts':{
			'title':{
				'size':20,
				'color inactive':'black',
				'color active':'dark green'
			},
			'desc':{
				'size':12,
				'color inactive':'black',
				'color active':'dark green'
			},
			'time':{
				'size':24,
				'color inactive':'black',
				'color active':'dark green'
			},
			'start':{
				'size':12,
				'color inactive':'green',
				'color active':'red',
				'width':4,
				'height':2
			}
		}
	}

	def __init__ (self, parent, timerdata=None, timersettings=None,
		bd=2, relief='raised', *args, **options):
		"""TimerButton constructor
		timer_data is the dict corresponding to the timer being created. title is the very-short
		description of the timer (<15 chars). description is a longer description and will be
		truncated appropriately.
		"""
		super().__init__(parent,bd=bd,relief=relief,*args,**options)

		# Initialize the callbacks array for when the toggle function is called
		self._toggle_callbacks = []

		# If the timerdata or settings parameters are given, use them so that we can modify
		# the values elsewhere in the program. If the parameters were not given, or were not
		# complete, use the default values.
		self._data = helper.dictFromDefaults(timerdata,self.DEFAULT_DATA)
		self._settings = helper.dictFromDefaults(timersettings,self.DEFAULT_SETTINGS)

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

		# Update the settings from the dicts
		self.update_data()
		self.update_settings()

	def _toggle (self):
		"""_toggle internal function
		Toggles the timer between running and paused.
		"""
		if self.running:
			self._start_button.configure(text=helper.PAUSE_CHAR)
			self._curr_start_time = time.time()
			self._timer_updater = self.after(500,self._update_timer)
			self.configure(relief='sunken')
		else:
			self._start_button.configure(text=helper.PLAY_CHAR)
			self.after_cancel(self._timer_updater)
			self._update_timer(restarttimer=False,storetime=True)
			self._curr_start_time = None
			self.configure(relief='raised')
		# Update the font colors
		self.update_settings()
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

	def _update_timer (self, restarttimer=True, storetime=False):
		"""_update_timer internal function
		Updates the label to the new time, as determined by the sum of the intervals in
		timer_data.intervals and the time between curr_start_time and time.time.
		Also, if storetime is True, stores the curr_start_time and time.time as a new interval.
		If restarttimer is True, it fires an after with a 500ms delay to call this function.
		"""
		# Grab the current time to compare to the start time
		end_time = time.time()
		# Store the interval, if desired
		if storetime:
			self._data['intervals'].append((self._curr_start_time,end_time))
		# Add up all the time from both the stored intervals and the current interval
		sum_time = 0
		for interval in self._data['intervals']:
			sum_time += interval[1]-interval[0]
		if self._curr_start_time and not storetime:
			sum_time += end_time - self._curr_start_time
		# Convert it to a readable time and store it in the label
		hours = int(sum_time/3600)
		minutes = int(sum_time/60)%60
		seconds = int(sum_time)%60
		new_text = '{:0>2}:{:0>2}:{:0>2}'.format(hours,minutes,seconds)
		self._timer_label.configure(text=new_text)
		# Setup the next timer
		if restarttimer:
			self._timer_updater = self.after(500,self._update_timer)

	def update_data (self):
		"""update_data function
		Updates the labels from the data attribute. Used when the user updates the title/desc.
		"""
		self._title_label.configure(text=self._data['title'])
		self._desc_label.configure(text=self._data['description'])

	def update_settings (self):
		"""update_settings function
		Updates the fonts from the settings attribute. Used when the user changes the settings.
		"""
		self._title_font.configure(size=self._settings['fonts']['title']['size'])
		self._desc_font.configure(size=self._settings['fonts']['desc']['size'])
		self._timer_font.configure(size=self._settings['fonts']['time']['size'])
		self._start_font.configure(size=self._settings['fonts']['start']['size'])
		self._start_button.configure(width=self._settings['fonts']['start']['width'],
			height=self._settings['fonts']['start']['height'])
		if self.running:
			self._title_label.configure(fg=self._settings['fonts']['title']['color active'])
			self._desc_label.configure(fg=self._settings['fonts']['desc']['color active'])
			self._timer_label.configure(fg=self._settings['fonts']['time']['color active'])
			self._start_button.configure(fg=self._settings['fonts']['start']['color active'])
		else:
			self._title_label.configure(fg=self._settings['fonts']['title']['color inactive'])
			self._desc_label.configure(fg=self._settings['fonts']['desc']['color inactive'])
			self._timer_label.configure(fg=self._settings['fonts']['time']['color inactive'])
			self._start_button.configure(fg=self._settings['fonts']['start']['color inactive'])

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
		def callback (atimer):
			if atimer.running:
				for timer in timers:
					if timer != atimer:
						timer.turn_off()
		def labelcallback (atimer):
			if atimer.running:
				atimer.turn_off()
		root = tk.Tk()
		timers = []
		timer_datas = [
			{'intervals':[(0,3500)],'title':"COE-4840",
				'description':"A really long, verbose, complicated pile of junk"},
			{'title':"Other timer",'description':"Some short text"},
			{'title':"Yet another timer",'description':"Words"}
		]
		timer_settings = {}
		frame = tk.Frame(root,width=400,height=200)
		frame.pack_propagate(False)
		frame.pack(fill='both',expand=True)
		for data in timer_datas:
			timer = TimerButton(frame, timerdata=data, timersettings=timer_settings)
			timer.pack(fill='x', expand=True)
			timer.register_toggle_callback(callback)
			timer.register_labelclick_callback(labelcallback)
			timers.append(timer)
		root.protocol('WM_DELETE_WINDOW',on_close)
		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")
