"""calendarwidget module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-31
Description = Provides the Calendar Tk widget. This widget provides a monthly calendar that allows
	navigation between months/years and selecting a day.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import calendar, time
# My code imports
import helper
from versionexception import VersionException

class Calendar (tk.Frame):
	"""Calendar class
	Displays a frame with a year, month, and days in the month. Buttons are provided to quickly
	change the month and year. Days are labels, but can be clicked to select them.
	"""
	OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
	DEFAULT_THEME = {
		'version':[1,0,0],
		'base':{
			'widget':{'bg':'SystemButtonFace',},
			'basic':{'fg':'black','bg':'SystemButtonFace',},
			'year':{},
			'month':{},
			'weekday':{'width':2,},
			'day':{
				'activebackground':'light grey',
				'borderwidth':1,
				'relief':'flat',
				'overrelief':'raised',
				'width':2,
			},
			'current day':{'bg':'light green',},
			'othermonth day':{'fg':'grey',},
			'nav buttons':{
				'height':1,
				'width':1,
				'relief':'flat',
				'overrelief':'raised',
			},
			'today button':{},
		},
		'active':{
			'day':{
				'borderwidth':1,
				'relief':'solid',
				'bg':'grey',
			},
		},
		'fonts':{
			'year':{'size':10,},
			'month':{'size':10,},
			'weekday':{'size':9,'weight':'bold',},
			'day':{'size':9,},
			'nav buttons':{'size':10,},
			'selected day':{'size':9,'weight':'bold',},
			'today button':{'size':10,},
		}
	}

	def _theme_version_update (self, oldtheme):
		"""_theme_version_update internal function
		Updates the old theme to the new format, based on relative versions.
		"""
		# Check for versions which are incompatible with list-of-numbers versions
		try:
			oldtheme['version'] < [0]
		except:
			raise VersionException(VersionException.BAD_TYPE,oldtheme['version'])

		# If the data version is later than the program version, we will not know how to convert
		if oldtheme['version'] > Calendar.DEFAULT_THEME['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldtheme['version'],Calendar.DEFAULT_THEME['version'])

		# If the old version is too old, we will not know how to convert
		if oldtheme['version'] < Calendar.OLDEST_CONVERTIBLE_THEME_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldtheme['version'],Calendar.DEFAULT_THEME['version'])

		# Finally, convert incrementally through all the versions
		# Below is some sample code to copy:
		#if oldtheme['version'] < [1,1]:
		#	oldtheme['somevariable'] = oldtheme['oldvariable']
		#	oldtheme['version'] = [1,1]

	def __init__ (self, parent, calendartheme=None, *args, **options):
		"""Calendar constructor
		Builds the year, month, and day selectors as well as the Today button. Then populates
		them appropriately. The optional calendartheme parameter should be a dict of theming
		preferences. See DEFAULT_THEME for a sample. The leaves of the dict tree are Tk config
		values.
		"""
		super().__init__(parent,*args,**options)

		currtime = time.localtime()
		# Initialize internal variables
		# Array of callback functions for when the user clicks a day button
		self._selectday_callbacks = []
		# Viewed date is the year/month that is currently displayed in the widget's day selector
		self._viewed_date = [currtime.tm_year,currtime.tm_mon,currtime.tm_mday]
		# Selected date is the last day the user clicked on
		self._selected_date = [currtime.tm_year,currtime.tm_mon,currtime.tm_mday]

		# Update the calendartheme parameters (or set to defaults)
		self._theme = helper.dictVersionUpdate(calendartheme,self._theme_version_update,
			self.DEFAULT_THEME)

		# Create the fonts; no need to set anything, as they will be configured in update_theme
		self._year_font = tkfont.Font()
		self._month_font = tkfont.Font()
		self._day_font = tkfont.Font()
		self._nav_buttons_font = tkfont.Font()
		self._selected_day_font = tkfont.Font()
		self._today_button_font = tkfont.Font()
		self._weekday_font = tkfont.Font()
		# Build the viewed year label and buttons
		year_frame = tk.Frame(self)
		year_frame.pack()
		self._change_year_minus = tk.Button(year_frame,text=helper.LEFT_CHAR,
			font=self._nav_buttons_font,
			command=lambda self=self,yearadd=-1: self._change_day_list(yearadd=yearadd))
		self._change_year_minus.pack(side='left')
		self._change_year_label = tk.Label(year_frame,text='',font=self._year_font)
		self._change_year_label.pack(side='left')
		self._change_year_plus = tk.Button(year_frame,text=helper.RIGHT_CHAR,
			font=self._nav_buttons_font,
			command=lambda self=self,yearadd=1: self._change_day_list(yearadd=yearadd))
		self._change_year_plus.pack(side='left')
		# Build the viewed month label and buttons
		month_frame = tk.Frame(self)
		month_frame.pack()
		self._change_month_minus = tk.Button(month_frame,text=helper.LEFT_CHAR,
			font=self._nav_buttons_font,
			command=lambda self=self,monthadd=-1: self._change_day_list(monthadd=monthadd))
		self._change_month_minus.pack(side='left')
		self._change_month_label = tk.Label(month_frame,text='',font=self._month_font)
		self._change_month_label.pack(side='left')
		self._change_month_plus = tk.Button(month_frame,text=helper.RIGHT_CHAR,
			font=self._nav_buttons_font,
			command=lambda self=self,monthadd=1: self._change_day_list(monthadd=monthadd))
		self._change_month_plus.pack(side='left')
		# Build the grid of day buttons and day labels
		day_frame = tk.Frame(self)
		day_frame.pack()
		self._days = [
			[None for d in range(helper.NUM_WEEKDAYS)] for w in range(helper.MAX_WEEKS_IN_MONTH)]
		self._days_monthadd = [
			[0 for d in range(helper.NUM_WEEKDAYS)] for w in range(helper.MAX_WEEKS_IN_MONTH)]
		self._days_daynum = [
			[0 for d in range(helper.NUM_WEEKDAYS)] for w in range(helper.MAX_WEEKS_IN_MONTH)]
		self._weekdays = [None for d in range(helper.NUM_WEEKDAYS)]
		for d in range(helper.NUM_WEEKDAYS):
			self._weekdays[d] = tk.Label(day_frame,text=helper.WEEKDAYS_2_LETTER[d],
				font=self._weekday_font)
			self._weekdays[d].grid(row=1,column=d+1)
		for w in range(helper.MAX_WEEKS_IN_MONTH):
			for d in range(helper.NUM_WEEKDAYS):
				self._days[w][d] = tk.Button(day_frame,text='',font=self._day_font,
					command=lambda self=self,w=w,d=d: self._click_day(w,d))
				self._days[w][d].grid(row=w+2,column=d+1)
		# Finally, add the Today button
		self._today_button = tk.Button(self,text="Select Today",font=self._today_button_font,
			command=lambda self=self: self.select_today())
		self._today_button.pack()

		self.update_theme()
		self._change_day_list()

	def select_today (self):
		"""select_today function
		Changes the day list to the current month/year and selects today's date.
		"""
		# Update both viewed and selected dates to the current date
		currtime = time.localtime()
		self._viewed_date = [currtime.tm_year,currtime.tm_mon,currtime.tm_mday]
		self._selected_date = [currtime.tm_year,currtime.tm_mon,currtime.tm_mday]
		# Update the day list to the current year/month
		self._change_day_list()
		# Notify any listeners that we changed the selected day
		self._call_selectday_callbacks()

	def _change_day_list (self, monthadd=0, yearadd=0):
		"""_change_day_list internal function
		Updates the currently-viewed list of days to match the viewed month/year. The optional
		parameters monthadd and yearadd allow adjusting the month/year before updating the day
		list.
		"""
		# First adjust the viewed year/month
		self._viewed_date[1] += monthadd
		self._viewed_date[0] += yearadd
		while self._viewed_date[1] > 12:
			self._viewed_date[0] += 1
			self._viewed_date[1] -= 12
		while self._viewed_date[1] < 1:
			self._viewed_date[0] -= 1
			self._viewed_date[1] += 12

		# Update the month/year labels
		self._change_year_label.configure(text=str(self._viewed_date[0]))
		self._change_month_label.configure(
			text=str(helper.MONTHS_3_LETTER[self._viewed_date[1]-1]))

		# Figure out the first day DOW and number of days in the month for the current month/year
		calinfo = list(calendar.monthrange(self._viewed_date[0],self._viewed_date[1]))
		# The calendar module considers Monday to be 0 for some bizarre reason
		calinfo[0] += 1
		calinfo[0] %= 7
		# We need the same for the previous month
		prev_year = self._viewed_date[0]
		prev_month = self._viewed_date[1] - 1
		if prev_month < 1:
			prev_year -= 1
			prev_month += 12
		prevcalinfo = list(calendar.monthrange(prev_year,prev_month))
		prevcalinfo[0] += 1
		prevcalinfo[0] %= 7

		# Initialize indices for week number and weekday number
		w,d = 0,0
		# and the starting daynum for the previous month
		daynum = prevcalinfo[1] - calinfo[0] + 1
		# Add all the days from the previous month to fill out the start of this month's week
		while daynum <= prevcalinfo[1]:
			self._days[w][d].configure(text=str(daynum))
			self._days_monthadd[w][d] = -1
			self._days_daynum[w][d] = daynum
			daynum += 1
			d += 1
			if d >= helper.NUM_WEEKDAYS:
				d = 0
				w += 1
		# Now do all the days from the current month
		daynum = 1
		while daynum <= calinfo[1]:
			self._days[w][d].configure(text=str(daynum))
			self._days_monthadd[w][d] = 0
			self._days_daynum[w][d] = daynum
			daynum += 1
			d += 1
			if d >= helper.NUM_WEEKDAYS:
				d = 0
				w += 1
		# Finally, fill in the last week
		daynum = 1
		while w < helper.MAX_WEEKS_IN_MONTH:
			self._days[w][d].configure(text=str(daynum))
			self._days_monthadd[w][d] = 1
			self._days_daynum[w][d] = daynum
			daynum += 1
			d += 1
			if d >= helper.NUM_WEEKDAYS:
				d = 0
				w += 1

		self._update_active_theme()

	def _click_day (self, week, weekday):
		"""_click_day internal function
		Function called by the day buttons when they are clicked. week is the row of the button
		and weekday is the column of the button.
		"""
		daynum = self._days_daynum[week][weekday]
		monthadd = self._days_monthadd[week][weekday]
		# Jump to the currently-viewed month/year
		self._selected_date = self._viewed_date[:]
		# If we clicked on a previous month or next month day, then add the modifier
		self._selected_date[1] += monthadd
		if self._selected_date[1] > 12:
			self._selected_date[0] += 1
			self._selected_date[1] = 1
		elif self._selected_date[1] < 1:
			self._selected_date[0] -= 1
			self._selected_date[1] = 12
		# Select the specific date
		self._selected_date[2] = daynum
		# Move the current day list to match selected day (and update the theme)
		self._change_day_list(monthadd=monthadd)
		# Notify any listeners that we've clicked the day
		self._call_selectday_callbacks()

	def update_theme (self):
		"""update_theme function
		Updates the fonts/colors/styles from the theme attribute. Used when the user changes
		the theme.
		"""
		widgets = (
			(self._change_year_label,'basic'),
			(self._change_month_label,'basic'),
			(self._today_button,'basic'),
			(self._change_month_minus,'basic'),
			(self._change_month_plus,'basic'),
			(self._change_year_minus,'basic'),
			(self._change_year_plus,'basic'),
			(self,'widget'),
			(self._change_year_label,'year'),
			(self._change_month_label,'month'),
			(self._today_button,'today button'),
			(self._change_month_minus,'nav buttons'),
			(self._change_month_plus,'nav buttons'),
			(self._change_year_minus,'nav buttons'),
			(self._change_year_plus,'nav buttons'),
		)
		fontwidgets = (
			(self._year_font,'year'),
			(self._month_font,'month'),
			(self._weekday_font,'weekday'),
			(self._day_font,'day'),
			(self._nav_buttons_font,'nav buttons'),
			(self._selected_day_font,'selected day'),
			(self._today_button_font,'today button'),
		)
		for widget,name in widgets:
			helper.configThemeFromDict(widget,self._theme,'base',name)
		for widget,name in fontwidgets:
			helper.configThemeFromDict(widget,self._theme,'fonts',name)
		self._update_active_theme()

	def _update_active_theme (self):
		"""_update_active_theme internal function
		Updates the colors to active or inactive, based on the state of the timer.
		"""
		for w in range(len(self._days)):
			for d in range(len(self._days[w])):
				helper.configThemeFromDict(self._days[w][d],self._theme,'base','basic')
				self._days[w][d].configure(font=self._day_font)
				helper.configThemeFromDict(self._days[w][d],self._theme,'base','day')
				today = time.localtime()
				if self._viewed_date[0] == today.tm_year and self._viewed_date[1] == today.tm_mon \
					and self._days_monthadd[w][d] == 0 and self._days_daynum[w][d] == today.tm_mday:
					helper.configThemeFromDict(self._days[w][d],self._theme,'base','current day')
				if self._days_monthadd[w][d] != 0:
					helper.configThemeFromDict(self._days[w][d],self._theme,'base','othermonth day')
				elif self._is_selected_day(self._days_daynum[w][d]):
					self._days[w][d].configure(font=self._selected_day_font)
					helper.configThemeFromDict(self._days[w][d],self._theme,'active','day')

	def _is_selected_day (self, daynum):
		"""_is_selected_day internal function
		Checks if the given daynum, along with the viewed month/year, matches the selected date.
		If it does, return True. Otherwise, return False.
		"""
		if self._viewed_date[0] == self._selected_date[0] \
			and self._viewed_date[1] == self._selected_date[1] \
			and self._selected_date[2] == daynum:
			return True
		return False

	def register_selectday_callback (self, callback):
		"""register_selectday_callback function
		Registers a function which will be called whenever the selected day changes.
		"""
		self._selectday_callbacks.append(callback)

	def _call_selectday_callbacks (self):
		"""_call_selectday_callbacks internal function
		Calls all the previously-registered selectday callback functions.
		"""
		for f in self._selectday_callbacks:
			f(self,self._selected_date)

if __name__ == "__main__":
	import traceback
	try:
		def selectday_callback (widget, selected_date):
			print(selected_date)
		root = tk.Tk()
		cal = Calendar(root)
		cal.register_selectday_callback(selectday_callback)
		cal.pack()
		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")

