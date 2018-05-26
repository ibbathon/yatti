"""Provides the FieldBase base class for data types used by the DataEditor.
Each instance provides a Tk widget with helper functions to assist the DataEditor, including
field-specific validation, an indicator of whether the value has changed, a function to change
the text without triggering validation, and more.
Each inheriting class should implement its own _raw_to_viewable and _viewable_to_raw.
Author = Richard D. Fears
Created = 2017-10-28
"""

import tkinter as tk

class FieldBase (tk.Entry):
	"""Base class for all data types. Tk widget with helper functions to assist the DataEditor."""

	STATUS_UNTOUCHED = 0
	STATUS_SAVED = 1
	STATUS_UNSAVED = 2
	STATUS_BADVALUE = 3

	def __init__ (self, parent, font, fieldconfig, data=None):
		"""Initializes the field and sets the raw/viewable data.
		config is the dictionary of options used by DataEditor.
		data is either a single value or a list of other fields (for calculated)."""
		super().__init__(parent,font=font)
		valreg = self.register(self._validate_field)
		self.config(validate='key',validatecommand=(valreg,'%P'))
		self._field_config = fieldconfig
		self.status = self.STATUS_UNTOUCHED
		self._skip_validation = False
		self._update_callbacks = []
		self.set_raw(data)

	def _default_value (self):
		"""Returns the default value for this field type. Defined as a function so child classes
		can override default value without overriding init."""
		return ''

	def _validate_field (self, newval):
		"""Validation function which checks if the newly-entered value is valid.
		If the new value is valid, set status to UNSAVED. Otherwise, set it to BADVALUE.
		Either way, always accept the new value."""
		# If this was triggered from set_raw, do not change the status or the raw
		if self._skip_validation:
			return True
		self.viewable = newval
		# If we can successfully convert to raw data, then status should be UNSAVED
		if self._viewable_to_raw():
			self.status = self.STATUS_UNSAVED
			for cb in self._update_callbacks:
				cb()
		# Otherwise, the status should be BADVALUE
		else:
			self.status = self.STATUS_BADVALUE
		# Either way, accept the new value
		return True

	def set_raw (self, raw):
		"""Sets the internal raw value and then converts it to viewable form and puts it
		in the field text."""
		if raw == None:
			raw = self._default_value()
		self.raw = raw
		if self._raw_to_viewable():
			self._set_field_text()

	def _set_field_text (self):
		"""Set the field text from the viewable."""
		self._skip_validation = True
		state = self.cget('state')
		self.config(state='normal')
		if self.get() == "":
			self.insert(0,"blah")
		self.delete(0,tk.END)
		self.insert(0,self.viewable)
		self.config(state=state)
		self._skip_validation = False

	def _viewable_to_raw (self):
		"""Converts the viewable value to a raw value.
		Returns True if the conversion is successful, False otherwise."""
		self.raw = self.viewable
		return True

	def _raw_to_viewable (self):
		"""Converts the viewable value to a raw value.
		Returns True if the conversion is successful, False otherwise."""
		self.viewable = self.raw
		return True

	def register_update_callback (self, cb):
		"""Registers a given callback function to be called whenever the field text is
		updated to a valid value by the user."""
		self._update_callbacks.append(cb)

	def update_status (self, newstatus, oldstatuses**):
		"""Changes the field status to the given new status, executing all necessary changes
		in the process. If oldstatuses are given, it only changes the field status if the current
		status is one of the given old statuses."""
		pass

	def advance_status (self):
		"""Called when the DataEditor is saved. Advances from UNSAVED to SAVED and from SAVED
		to UNTOUCHED."""
		if self.status == self.STATUS_UNSAVED:
			self.status = self.STATUS_SAVED
		elif self.status == self.STATUS_SAVED:
			self.status = self.STATUS_UNTOUCHED

	def enable (self, enable):
		"""Enables/disables the entry."""
		if enable:
			self.config(state='normal')
		else:
			self.config(state='readonly')
		
	def test_class (fieldclass, testvalue=None):
		import tkinter.font as tkfont
		import traceback
		try:
			def update_callback ():
				print(field.raw,field.viewable)
			root = tk.Tk()
			font = tkfont.Font()
			field = fieldclass(root,font,None,testvalue)
			field.register_update_callback(update_callback)
			field.pack()
			root.mainloop()
		except Exception as e:
			print()
			traceback.print_exc()
		finally:
			input("Press enter to quit")

if __name__ == "__main__":
	FieldBase.test_class(FieldBase)
