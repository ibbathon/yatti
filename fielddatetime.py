"""Provides the FieldDatetime class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import time
import fieldbase, helper

class FieldDatetime (fieldbase.FieldBase):
    """FieldDatetime widget for DataEditor."""

    def _default_value (self):
        """Returns current datetime, default value for datetime."""
        return time.time()

    def _viewable_to_raw (self):
        """Converts the viewable datetime to a Unix epoch time.
        Returns True if the conversion is successful, False otherwise."""
        try:
            self.raw = time.mktime(
                time.strptime(self.viewable,helper.DATETIME_FORMAT)
            )
            return True
        except:
            return False

    def _raw_to_viewable (self):
        """Converts the Unix epoch time to a viewable datetime.
        Returns True if the conversion is successful, False otherwise."""
        try:
            self.viewable = time.strftime(
                helper.DATETIME_FORMAT,time.localtime(self.raw)
            )
            return True
        except:
            return False


if __name__ == "__main__":
    FieldDatetime.test_class(FieldDatetime)
