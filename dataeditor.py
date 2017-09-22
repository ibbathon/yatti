"""dataeditor module
Author = Richard D. Fears
Created = 2017-09-10
Description = Provides the DataEditor Tk widget. This widget provides a grid of descriptions
	and labels for editing a single-level dictionary.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import time
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
			'entries':{},
			'checkboxes':{},
			'buttons':{},
			'save button':{},
		},
		'active':{},
		'fonts':{
			'labels':{'size':10},
			'entries':{'size':10},
			'buttons':{'size':8},
			'save button':{'size':12},
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
		if oldtheme['version'] > DataEditor.DEFAULT_THEME['version']:
			raise VersionException(VersionException.TOO_NEW,
				oldtheme['version'],DataEditor.DEFAULT_THEME['version'])

		# If the old version is too old, we will not know how to convert
		if oldtheme['version'] < DataEditor.OLDEST_CONVERTIBLE_THEME_VERSION:
			raise VersionException(VersionException.TOO_OLD,
				oldtheme['version'],DataEditor.DEFAULT_THEME['version'])

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
		The valid types are string, datetime, boolean, float, integer, and table. The 'key' field
		refers to the key in the dictionary that will be used to populate these entries.
		"""
		super().__init__(parent,*args,**options)

		# Initialize internal variables
		# Array of callback functions for when a save occurs
		self._save_callbacks = []
		# Data dict
		self._data = None
		# Whether to enable/disable root fields and table fields
		self._root_field_state = 'readonly'
		self._table_field_state = 'readonly'
		self._table_button_state = 'disabled'
		self._save_button_state = 'disabled'

		# Update the dataeditortheme parameters (or set to defaults)
		self._theme = helper.dictVersionUpdate(dataeditortheme,self._theme_version_update,
			self.DEFAULT_THEME)

		# Create the fonts; no need to set anything, as they will be configured in update_theme
		self._labels_font = tkfont.Font()
		self._entries_font = tkfont.Font()
		self._buttons_font = tkfont.Font()
		self._save_button_font = tkfont.Font()
		# Build the labels and entries
		self._conf = conf
		for i,field in enumerate(self._conf):
			field['label'] = tk.Label(self,text=field['text'],font=self._labels_font)
			field['label'].grid(column=0,row=i,sticky='ne')
			# One-row fields
			if field['type'] != 'table':
				field['entry'] = tk.Entry(self,font=self._entries_font,state=self._root_field_state)
				field['entry'].grid(column=1,row=i,sticky='w')
			# Multi-row/column fields
			else:
				field['frame'] = tk.Frame(self)
				field['frame'].grid(column=1,row=i,sticky='w')
				for j,subfield in enumerate(field['columns']):
					subfield['label'] = tk.Label(field['frame'],text=subfield['text'],
						font=self._labels_font)
					subfield['label'].grid(column=j,row=0,sticky='ew')
					subfield['rows'] = []
					subfield['rows'].append(tk.Entry(field['frame'],font=self._entries_font,
						state=self._table_field_state))
					subfield['rows'][-1].grid(column=j,row=1,sticky='ew')
				field['buttons'] = [] # Don't need buttons until we have data
		# Finally, tack on the save button
		self._save_button = tk.Button(self,text="Save",font=self._save_button_font,
			command=self.save_data,state=self._save_button_state)
		self._save_button.grid(column=0,row=len(self._conf))

		self.update_theme()

	def _convert_field_to_data (self, fieldentry, fieldindex, columnindex=-1):
		"""_convert_field_to_data internal function
		Converts the given text to the indicated field's/column's type. Returns None if it
		failed to convert.
		"""
		fieldvalue = fieldentry.get()
		# If a table, grab the column's type; otherwise, grab the field's type
		field = self._conf[fieldindex]
		if field['type'] == 'table':
			fieldtype = field['columns'][columnindex]['type']
		else:
			fieldtype = field['type']

		# Convert fieldvalue from str to the desired type, based on the field type
		if fieldtype == 'boolean':
			if fieldvalue.lower() in ("true","1"):
				datavalue = True
			elif fieldvalue.lower() in ("false","0"):
				datavalue = False
			else:
				return None
		elif fieldtype == 'float':
			try:
				datavalue = float(fieldvalue)
			except:
				return None
		elif fieldtype == 'integer':
			try:
				datavalue = int(fieldvalue)
			except:
				return None
		elif fieldtype == 'datetime':
			try:
				datavalue = time.mktime(time.strptime(fieldvalue,helper.DATE_FORMAT))
			except:
				return None
		else:
			# Assume string with no conversion
			datavalue = fieldvalue

		return datavalue

	def _convert_data_to_field (self, datavalue, fieldindex, columnindex=-1):
		"""_convert_data_to_field internal function
		Converts the given value to an appropriate string, given the indicated
		field's/column's type. Returns None if it failed to convert.
		"""
		# If a table, grab the column's type; otherwise, grab the field's type
		field = self._conf[fieldindex]
		if field['type'] == 'table':
			fieldtype = field['columns'][columnindex]['type']
		else:
			fieldtype = field['type']

		# Convert datavalue from the type to string
		if fieldtype == 'datetime':
			try:
				fieldvalue = time.strftime(helper.DATE_FORMAT,time.localtime(datavalue))
			except:
				return None
		else:
			# Assume default string conversion
			fieldvalue = str(datavalue)

		return fieldvalue

	def _delete_row (self, fieldindex, rowindex):
		"""_delete_row internal function
		Deletes a row from a table field.
		"""
		# Delete the data from the data dict
		datakey = self._conf[fieldindex]['key']
		del self._data[datakey][rowindex]
		self._rebuild_table(fieldindex)

	def _add_row (self, fieldindex):
		"""_add_row internal function
		Adds a row to the end of the grid for the given table field.
		"""
		# Construct the new row based on defaults for the column types
		field = self._conf[fieldindex]
		newrow = []
		for column in field['columns']:
			if column['type'] == 'boolean':
				newrow.append(False)
			elif column['type'] == 'float':
				newrow.append(0.0)
			elif column['type'] == 'integer':
				newrow.append(0)
			elif column['type'] == 'datetime':
				newrow.append(time.time())
			else:
				newrow.append('')
		# Add the row to the data dict and then refresh the view of it
		datakey = field['key']
		self._data[datakey].append(newrow)
		self._rebuild_table(fieldindex)

	def _rebuild_table (self, fieldindex, initial=False):
		"""_rebuild_table internal function
		Removes all the entry widgets from the given table and then readds based on the data.
		"""
		field = self._conf[fieldindex]
		# Delete entries
		for subfield in field['columns']:
			for row in subfield['rows']:
				row.destroy()
			subfield['rows'] = []
		# Delete add/delete buttons
		for i in range(len(field['buttons'])):
			field['buttons'][i].destroy()
		field['buttons'] = []
		# Re-add entries
		datakey = field['key']
		for i,subfield in enumerate(field['columns']):
			for j,row in enumerate(self._data[datakey]):
				if subfield['type'] == 'boolean':
					subfield['rows'].append(tk.Entry(field['frame'],width=5,
						font=self._entries_font,state=self._table_field_state))
				else:
					subfield['rows'].append(tk.Entry(field['frame'],
						font=self._entries_font,state=self._table_field_state))
				self._read_data(fieldindex,i,j)
				subfield['rows'][-1].grid(column=i,row=j+1,sticky='ew')
		# Re-add buttons
		for j in range(len(self._data[datakey])):
			field['buttons'].append(
				tk.Button(field['frame'],text='-',font=self._buttons_font,
					state=self._table_button_state,
					command=lambda self=self,fieldindex=fieldindex,rowindex=j:
						self._delete_row(fieldindex,rowindex)))
			field['buttons'][-1].grid(column=len(field['columns'])+1,row=j+1)
		field['buttons'].append(
			tk.Button(field['frame'],text='+',font=self._buttons_font,
				state=self._table_button_state,
				command=lambda self=self,fieldindex=fieldindex:self._add_row(fieldindex)))
		field['buttons'][-1].grid(
			column=0,row=len(self._data[datakey])+1,columnspan=len(field['columns'])+1)
		# Refresh the theme if this is not being called from the data setup function
		if not initial:
			self.update_theme()

	def _refresh_table (self, fieldindex):
		"""_refresh_table internal function
		Re-reads the data from data dict into the given table.
		"""
		field = self._conf[fieldindex]
		datakey = field['key']
		for i,subfield in enumerate(field['columns']):
			for j,row in enumerate(subfield['rows']):
				self._read_data(fieldindex,i,j)

	def _read_data (self, fieldindex, column=-1, row=-1):
		"""_read_data internal function
		Reads from the data dict and constructs a string to place in the indicated entry widget.
		"""
		field = self._conf[fieldindex]
		datakey = field['key']
		if field['type'] == 'table':
			entrywidget = field['columns'][column]['rows'][row]
			datavalue = self._data[datakey][row][column]
			fieldvalue = self._convert_data_to_field(datavalue,fieldindex,column)
		else:
			entrywidget = field['entry']
			datavalue = self._data[datakey]
			fieldvalue = self._convert_data_to_field(datavalue,fieldindex)

		# If we failed to convert, default to empty string
		if fieldvalue == None:
			fieldvalue = ""

		state = entrywidget.cget('state')
		entrywidget.config(state='normal')
		if entrywidget.get() == "":
			entrywidget.insert(0,"blah")
		entrywidget.delete(0,tk.END)
		entrywidget.insert(0,fieldvalue)
		entrywidget.config(state=state)

	def _write_data (self, newvalue, fieldindex, column=-1, row=-1):
		"""_write_data internal function
		If newvalue is provided, this just stores the value in the data dict. Otherwise, it tries
		to convert it to the correct format first and then store it.
		Returns True if it succeeded in converting/storing; False otherwise.
		"""
		field = self._conf[fieldindex]
		# Place the new value in the data and then re-read it so the user sees the change
		datakey = field['key']
		if field['type'] == 'table':
			self._data[datakey][row][column] = newvalue
		else:
			self._data[datakey] = newvalue
		self._read_data(fieldindex,column,row)
		return True

	def load_data (self, data):
		"""load_data function
		Loads the provided data dict into the fields.
		"""
		self._data = data
		for i,field in enumerate(self._conf):
			if field['key'] not in self._data:
				self._data[field['key']] = ''

			if field['type'] == 'table':
				self._rebuild_table(i,initial=True)
			else:
				self._read_data(i)

		self.update_theme()

	def save_data (self):
		"""save_data function
		Converts and saves the field text to the data dict. If anything fails to convert,
		it does not store the new data. Either way, it calls any registered save callback
		functions with a list of error dicts.
		"""
		# Convert each text field to the appropriate type, and store the value in a temp var
		errors = []
		for i,field in enumerate(self._conf):
			if field['type'] != 'table':
				field['convertedvalue'] = self._convert_field_to_data(field['entry'],i)
				if field['convertedvalue'] == None:
					errors.append({
						'label':field['text'],
						'key':field['key'],
						'tableindex':(0,0),
						'type':field['type'],
						'badtext':field['entry'].get()
					})
			else:
				for j,subfield in enumerate(field['columns']):
					subfield['convertedvalues'] = [None for k in range(len(subfield['rows']))]
					for k,row in enumerate(subfield['rows']):
						subfield['convertedvalues'][k] = self._convert_field_to_data(row,i,j)
						if subfield['convertedvalues'][k] == None:
							errors.append({
								'label':field['text'],
								'key':field['key'],
								'tableindex':(k,j),
								'type':subfield['type'],
								'badtext':row.get()
							})

		# If no errors, write the converted values to the data dict
		if len(errors) == 0:
			for i,field in enumerate(self._conf):
				if field['type'] != 'table':
					self._write_data(field['convertedvalue'],i)
				else:
					for j,subfield in enumerate(field['columns']):
						for k,row in enumerate(subfield['rows']):
							self._write_data(subfield['convertedvalues'][k],i,j,k)

		# Let registered functions know that we finished
		for f in self._save_callbacks:
			f(errors)

	def clear_data (self):
		"""clear_data function
		Simply sets the internal data dict to None and disables all fields.
		This should be called anytime the underlying data is deleted.
		"""
		self._data = None
		self.enable(rootfields=False)

	def register_save_callback (self, function):
		"""register_save_callback function
		Registers a function which will be called when the save finishes.
		The function should accept one parameter, a list of error dictionaries. Each error dict
		contains the following keys: label, key, tableindex, type, and badtext.
		"""
		self._save_callbacks.append(function)

	def update_theme (self):
		"""update_theme function
		Updates the fonts/colors/styles from the theme attribute. Used when the user changes
		the theme.
		"""
		# Update fonts
		helper.configThemeFromDict(self._entries_font,self._theme,'fonts','entries')
		helper.configThemeFromDict(self._labels_font,self._theme,'fonts','labels')
		helper.configThemeFromDict(self._buttons_font,self._theme,'fonts','buttons')
		helper.configThemeFromDict(self._save_button_font,self._theme,'fonts','save button')
		helper.configThemeFromDict(self._save_button,self._theme,'base','save button')
		# Update widgets
		for field in self._conf:
			helper.configThemeFromDict(field['label'],self._theme,'base','labels')
			if field['type'] != 'table':
				helper.configThemeFromDict(field['entry'],self._theme,'base','entries')
			else:
				for subfield in field['columns']:
					helper.configThemeFromDict(subfield['label'],self._theme,'base','labels')
					for row in subfield['rows']:
						helper.configThemeFromDict(row,self._theme,'base','entries')
				for button in field['buttons']:
					helper.configThemeFromDict(button,self._theme,'base','buttons')

	def update_data (self):
		"""update_data function
		Updates the data for all keys.
		"""
		if self._data == None:
			return
		for field in self._conf:
			self.update_data_for_key(field['key'])

	def update_data_for_key (self, key):
		"""update_data_for_key function
		Updates the data for a single key, allowing running timers to update the data editor.
		"""
		if self._data == None:
			return
		for i,field in enumerate(self._conf):
			if field['key'] == key:
				if field['type'] == 'table':
					# Rebuild if the data has different number of rows than the entries
					if len(field['columns'][0]['rows']) != len(self._data[key]):
						self._rebuild_table(i)
					else:
						self._refresh_table(i)
				else:
					self._read_data(i)

	def enable (self, rootfields=True, tables=None):
		"""enable function
		Enables/disables the entry fields. rootfields controls everything but tables.
		tables controls the tables. If tables is not provided, assume same setting as rootfields.
		"""
		if tables == None:
			tables = rootfields
		if rootfields:
			self._root_field_state = 'normal'
			self._save_button_state = 'normal'
		else:
			self._root_field_state = 'readonly'
			self._save_button_state = 'disabled'
		if tables:
			self._table_field_state = 'normal'
			self._table_button_state = 'normal'
		else:
			self._table_field_state = 'readonly'
			self._table_button_state = 'disabled'

		self._toggle_states()

	def _toggle_states (self):
		"""_toggle_states internal function
		Sets each field/button to enabled or disabled based on the internal variables.
		"""
		for field in self._conf:
			if field['type'] == 'table':
				for subfield in field['columns']:
					for row in subfield['rows']:
						row.configure(state=self._table_field_state)
				for button in field['buttons']:
					button.configure(state=self._table_button_state)
			else:
				field['entry'].configure(state=self._root_field_state)
		self._save_button.config(state=self._save_button_state)

if __name__ == "__main__":
	import traceback, json
	try:
		def save_callback (errors):
			global label
			label.config(text=str(len(errors))+" errors")
			if len(errors) == 0:
				label.config(fg='black')
			else:
				label.config(fg='red')
			print(json.dumps(data,indent='\t',separators=(', ',':')))
		root = tk.Tk()
		config = [
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
		data = {
			"source system":"YATTi", "intervals":[
				[1505221371.8944616,1505221375.320189,False,""],
				[1505222275.3718667,1505222283.2568984,False,""]
			], "description":"Default timer", "title":"TIMER", "version":[1,0,0]
		}
		de = DataEditor(root,config)
		de.pack()
		de.register_save_callback(save_callback)
		de.load_data(data)
		de.enable()
		label = tk.Label(root,text=" ")
		label.pack()
		root.mainloop()
	except Exception as e:
		print()
		traceback.print_exc()
	finally:
		input("Press enter to quit")


