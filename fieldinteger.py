"""Provides the FieldInteger class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import fieldbase

class FieldInteger (fieldbase.FieldBase):
	"""FieldInteger widget for DataEditor."""

	def _default_value (self):
		"""Returns 0, default integer value."""
		return 0

	def _viewable_to_raw (self):
		"""Converts the viewable string to an integer.
		Returns True if the conversion is successful, False otherwise."""
		try:
			self.raw = int(self.viewable)
			return True
		except:
			return False

	def _raw_to_viewable (self):
		"""Converts the integer to a viewable string.
		Returns True if the conversion is successful, False otherwise."""
		try:
			self.viewable = str(self.raw)
			return True
		except:
			return False


if __name__ == "__main__":
	FieldInteger.test_class(FieldInteger)
