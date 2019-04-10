"""Provides the FieldString class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import fieldbase

class FieldString (fieldbase.FieldBase):
    """FieldString widget for DataEditor."""
    # This is basically just a wrapper for FieldBase, as that class's defaults
    # are sufficient
    pass


if __name__ == "__main__":
    FieldString.test_class(FieldString)
