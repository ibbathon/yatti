"""Provides the FieldFloat class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import fieldbase

class FieldFloat (fieldbase.FieldBase):
    """FieldFloat widget for DataEditor."""

    def _default_value (self):
        """Returns 0.0, default float value."""
        return 0.0

    def _viewable_to_raw (self):
        """Converts the viewable string to a float.
        Returns True if the conversion is successful, False otherwise."""
        try:
            self.raw = float(self.viewable)
            return True
        except:
            return False

    def _raw_to_viewable (self):
        """Converts the float to a viewable string.
        Returns True if the conversion is successful, False otherwise."""
        try:
            self.viewable = str(self.raw)
            return True
        except:
            return False


if __name__ == "__main__":
    FieldFloat.test_class(FieldFloat)
