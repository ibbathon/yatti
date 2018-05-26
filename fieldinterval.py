"""Provides the FieldInterval class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import time
import fieldbase, helper

class FieldInterval (fieldbase.FieldBase):
	"""FieldInterval widget for DataEditor."""

	def __init__ (self, parent, font, fieldconfig, data):
		"""Initializes the field and calculates the raw from the provided other nodes.
		data must be a list of length 2 with elements being two other FieldBases, preferably
		(but not necessarily) FieldDatetimes.
		fieldconfig is the dictionary of options used by DataEditor."""
		self._sources = data
		for source in self._sources:
			source.register_update_callback(self.calculate_raw_from_sources)
		self.calculate_raw_from_sources(preinit=True)
		data = self.raw
		super().__init__(parent,font,fieldconfig,data)

	def calculate_raw_from_sources (self, preinit=False, automatic=False):
		"""Calculates the raw interval length by subtracting the first source's raw from the
		second source's raw."""
		self.raw = self._sources[1].raw - self._sources[0].raw
		if not preinit:
			self._raw_to_viewable()
			if not automatic:
				self.status = self.STATUS_UNSAVED
			self._set_field_text()

	def _viewable_to_raw (self):
		"""Converts the viewable time to an interval length using time and some manipulation.
		Also sets the raw value of the second source node to the sum of the interval length
		and the raw value of the first source node.
		Returns True if the conversion is successful, False otherwise."""
		try:
			shiftedinterval = time.mktime(time.strptime(
				helper.START_OF_TIME+helper.DATE_TIME_SPACER+self.viewable,
				helper.DATETIME_FORMAT
			))
			shiftedstartoftime = time.mktime(time.gmtime(0))
			self.raw = shiftedinterval-shiftedstartoftime
			self._sources[1].set_raw(self._sources[0].raw+self.raw)
			self._sources[1].status = self.STATUS_UNSAVED
			return True
		except:
			return False

	def _raw_to_viewable (self):
		"""Converts the interval length to a viewable time.
		Returns True if the conversion is successful, False otherwise."""
		try:
			self.viewable = time.strftime(helper.TIME_FORMAT,time.gmtime(self.raw))
			return True
		except:
			return False

	def test_class (fieldclass, testvalue=None):
		import fielddatetime
		import tkinter as tk
		import tkinter.font as tkfont
		import traceback
		try:
			def update_callback ():
				print(source[0].raw,source[0].viewable)
				print(source[1].raw,source[1].viewable)
				print(field.raw,field.viewable)
			root = tk.Tk()
			font = tkfont.Font()
			source = [None,None]
			source[0] = fielddatetime.FieldDatetime(root,font,None)
			if testvalue != None:
				source[1] = fielddatetime.FieldDatetime(root,font,None,source[0].raw+testvalue)
			else:
				source[1] = fielddatetime.FieldDatetime(root,font,None)
			field = fieldclass(root,font,None,source)
			source[0].register_update_callback(update_callback)
			source[1].register_update_callback(update_callback)
			field.register_update_callback(update_callback)
			source[0].pack()
			source[1].pack()
			field.pack()
			root.mainloop()
		except Exception as e:
			print()
			traceback.print_exc()
		finally:
			input("Press enter to quit")


if __name__ == "__main__":
	FieldInterval.test_class(FieldInterval)
