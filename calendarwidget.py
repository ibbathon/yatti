"""calendarwidget module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-23
Description = Provides the Calendar Tk widget. This widget provides a monthly calendar that allows
	navigation between months/years and selecting a day.
"""
import tkinter as tk
import tkinter.font as tkfont
import calendar
import time

class Calendar (tk.Frame):
	"""Calendar class
	Displays a frame with a year, month, and days in the month. Buttons are provided to quickly
	change the month and year. Days are labels, but can be clicked to select them.
	"""

	DEFAULT_THEME = {
		'base':{
			'widget':{},
			'basic':{'fg':'black','bg':'white',},
			'year':{},
			'month':{},
			'day':{
				'activebackground':'light grey',
				'borderwidth':0,
				'relief':'flat',
			},
			'nav buttons':{},
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
			'widget':{},
			'year':{'size':10,},
			'month':{'size':10,},
			'day':{'size':9,},
			'nav buttons':{'size':10,},
			'selected day':{},
			'today button':{},
		}
	}

	def __init__ (self, parent, *args, **options):
		"""Calendar constructor
		"""
		super().__init__(parent,*args,**options)

		self._todays_date = time.localtime()
		self._viewed_date = time.localtime()
		self._selected_date = None

		self.update_theme()

	def _change_day_list (self, monthadd=0, yearadd=0):
		"""_build_day_list internal function
		"""
		# First adjust the viewed year/month
		self._viewed_date.tm_mon += monthadd
		self._viewed_date.tm_year += yearadd
		while self._viewed_date.tm_mon > 12:
			self._viewed_date.tm_year += 1
			self._viewed_date.tm_mon -= 12
		while self._viewed_date.tm_mon < 1:
			self._viewed_date.tm_year -= 1
			self._viewed_date.tm_mon += 12

	def update_theme (self):
		"""update_theme function
		Updates the fonts/colors/styles from the theme attribute. Used when the user changes
		the theme.
		"""
		widgets = {'widget':self}
		fontwidgets = {}
		for name,widget in widgets.items():
			helper.configThemeFromDict(widget,self._theme,'base',name)
		for name,widget in fontwidgets.items():
			helper.configThemeFromDict(widget,self._theme,'fonts',name)
		self._update_active_theme()

	def _update_active_theme (self):
		"""_update_active_theme internal function
		Updates the colors to active or inactive, based on the state of the timer.
		"""
		widgets = {'widget':self}
		if self.running:
			for name,widget in widgets.items():
				helper.configThemeFromDict(widget,self._theme,'active',name)
		else:
			for name,widget in widgets.items():
				helper.configThemeFromDict(widget,self._theme,'base',name)


if __name__ == "__main__":
	import traceback
	try:
		root = tk.Tk()
		cal = Calendar(root)
		cal.pack()
		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")

