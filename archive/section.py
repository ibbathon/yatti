"""section module
Author = Richard D. Fears
Created = 2017-08-17
LastModified = 2017-08-17
Description = Provides the Section Tk class, which is a container widget allowing you to have
	expandable sections.
"""
import tkinter as tk

class Section (tk.Frame):
	"""Section class
	A widget which acts as an expandable section. Children added to this widget's sub_frame will
	be displayed when the section is expanded, and hidden when it is collapsed.
	"""
	# TODO: Expand the capabilities to allow customizing the appearance of the title frame

	def __init__ (self, parent, text="", indent_level=10, *args, **options):
		"""Section constructor
		text is the title of the section. All other parameters are the same as for Frame.
		"""
		super().__init__(parent,*args,**options)

		# Variable for whether or not the section is currently expanded
		self._expanded = False

		# Store how indented the children should be
		self._indent_level = indent_level

		# Header frame for the section
		self._title_frame = tk.Frame(self, relief='solid', borderwidth=1)
		self._title_frame.pack(fill='x',expand=True)

		# The +/- button (label)
		self._toggle_button = tk.Label(self._title_frame, width=2, text='+')
		self._toggle_button.bind('<Button-1>', lambda e,self=self: self._toggle())
		self._toggle_button.pack(side='left')
		# Title of the section
		title_text = tk.Label(self._title_frame, text=text)
		title_text.bind('<Button-1>', lambda e,self=self: self._toggle())
		title_text.pack(side='left', fill='x', expand=True)

		# Create the frame used by all children
		self.sub_frame = tk.Frame(self)

	def _toggle (self):
		"""_toggle internal function
		Hides or shows the sub_frame, based on the current state.
		"""
		if self._expanded:
			self._expanded = False
		else:
			self._expanded = True
		if self._expanded:
			self.sub_frame.pack(fill='x', expand=True, padx=(self._indent_level,0), anchor='w')
			self._toggle_button.configure(text='-')
		else:
			self.sub_frame.pack_forget()
			self._toggle_button.configure(text='+')


if __name__ == "__main__":
	import traceback
	try:
		root = tk.Tk()
		section1 = Section(root, text="Section 1")
		section1.pack(fill='x', expand=True, anchor='nw')
		first_line = tk.Frame(section1.sub_frame)
		first_line.pack(fill='x', expand=True)
		tk.Label(first_line, text="Some words:").pack(side='left', fill='x', expand=True)
		tk.Entry(first_line).pack(side='left')

		section1a = Section(section1.sub_frame, text="Section 1a")
		section1a.pack(fill='x', side='top', expand=True, anchor='nw')
		tk.Label(section1a.sub_frame, text="More words").pack(anchor='w')

		section1b = Section(section1.sub_frame, text="Section 1b")
		section1b.pack(fill='x', side='top', expand=True, anchor='nw')
		tk.Label(section1b.sub_frame, text="Even more words").pack(anchor='w')

		section2 = Section(root, text="Section 2")
		section2.pack(fill='x', expand=True, anchor='nw')
		for i in range(10):
			tk.Label(section2.sub_frame, text="Text "+str(i)).pack(anchor='w')

		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
		input("Press enter to quit")
