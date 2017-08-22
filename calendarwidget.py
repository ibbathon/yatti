"""calendarwidget module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-22
Description = Provides the Calendar Tk widget. This widget provides a monthly calendar that allows
	navigation between months/years and selecting a day.
"""
import tkinter as tk
import tkinter.font as tkfont
import calendar

class Calendar (tk.Frame):
	"""Calendar class
	Displays a frame with a year, month, and days in the month. Buttons are provided to quickly
	change the month and year. Days are labels, but can be clicked to select them.
	"""

	def __init__ (self, parent, *args, **options):
		"""Calendar constructor
		"""
		super().__init__(parent,*args,**options)

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

