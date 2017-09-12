"""dataeditor module
Author = Richard D. Fears
Created = 2017-09-10
LastModified = 2017-09-10
Description = Provides the DataEditor Tk widget. This widget provides a grid of descriptions
	and labels for editing a single-level dictionary.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports

# My code imports
import helper
from versionexception import VersionException

class DataEditor (tk.Frame):
	"""DataEditor class
	Displays a frame with a grid of labels and text boxes for editing a single-level dictionary.
	"""
	OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
	DEFAULT_THEME = {
		'version':[1,0,0],
		'base':{
			'widget':{'bg':'SystemButtonFace',},
			'basic':{'fg':'black','bg':'SystemButtonFace',},
			'labels':{},
			'textboxes':{},
			'checkboxes':{},
		},
		'active':{},
		'fonts':{
			'labels':{'size':12},
			'textboxes':{'size':12},
		},
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

	def __init__ (self, parent, conf, dataeditortheme=None, *args, **options):
		"""DataEditor constructor
		Builds a grid of labels and text boxes based on the provided configuration. The text
		boxes can later be populated/disabled/enabled/updated by other functions.
		The optional dataeditortheme parameter should be a dict of theming preferences. See
		DEFAULT_THEME for a sample. The leaves of the dict tree are Tk config values.
		conf is the important parameter here and has a format similar to the following:
		[
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
		Note that you cannot recursively build tables... yet.
		The valid types are string, datetime, boolean, float, number, and table. The 'key' field
		refers to the key in the dictionary that will be used to populate these textboxes.
		"""
		super().__init__(parent,*args,**options)

		# Initialize internal variables
		# Array of callback functions for when the user edits a textbox
		self._edittext_callbacks = []
		# Validation function which triggers when any of the textboxes are changed
		self._validation_reg = self.register(self._validation)

		# Update the dataeditortheme parameters (or set to defaults)
		self._theme = helper.dictVersionUpdate(dataeditortheme,self._theme_version_update,
			self.DEFAULT_THEME)

		# Create the fonts; no need to set anything, as they will be configured in update_theme
		self._labels_font = tkfont.Font()
		self._textboxes_font = tkfont.Font()
		# Build the labels and textboxes
		self._conf = conf
		for i,field in enumerate(self._conf):
			field['label'] = tk.Label(self,text=field['text'],font=self._labels_font)
			field['label'].grid(column=0,row=i,sticky='e')
			if field['type'] != 'table':
				field['entry'] = tk.Entry(self,font=self._textboxes_font,validate='all',
					state='readonly',validatecommand=(
						lambda a,iv,nv,at,self=self,i=i: self._validation_reg(a,iv,nv,at,i),
						'%d','%s','%P','%V'))
				field['entry'].grid(column=1,row=i,sticky='w')
			else:
				field['frame'] = tk.Frame(self)
				field['frame'].grid(column=1,row=i,sticky='w')
				for j,subfield in enumerate(field['columns']):
					subfield['label'] = tk.Label(field['frame'],text=subfield['text'],
						font=self._labels_font)
					subfield['label'].grid(column=i,row=0,sticky='ew')
					subfield['entry'] = tk.Entry(field['frame'],font=self._textboxes_font,
						validate='all',state='readonly',validatecommand=(
							lambda a,iv,nv,at,self=self,i=i,j=j:
								self._validation_reg(a,iv,nv,at,i,j),'%d','%s','%P','%V'))
					subfield['entry'].grid(column=i,row=1,sticky='ew')

		self.update_theme()

	def _validation (self,action,initialvalue,newvalue,actiontype,fieldindex,subfieldindex=0):
		"""_validation internal function
		Entry validation function. If the value has changed, it changes the corresponding
		dictionary field and then calls any callback functions.
		"""
		if self._dict != None

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


