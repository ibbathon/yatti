"""Provides the FieldBoolean class for the DataEditor.
Author = Richard D. Fears
Created = 2017-10-28
"""

import tkinter as tk

class FieldBoolean (tk.Checkbutton):
    """Field class for boolean data types for the DataEditor."""

    STATUS_UNTOUCHED = 0
    STATUS_SAVED = 1
    STATUS_UNSAVED = 2
    STATUS_BADVALUE = 3

    def __init__ (self, parent, font, fieldconfig, data=None):
        """Initializes the field and sets the raw/viewable data.
        config is the dictionary of options used by DataEditor.
        data is a single boolean value."""
        super().__init__(parent,font=font)
        self._boolvar = tk.BooleanVar()
        self._boolvar.trace('w',self._validate_field)
        self.config(variable=self._boolvar)
        self._field_config = fieldconfig
        self.status = self.STATUS_UNTOUCHED
        self._skip_validation = False
        self._update_callbacks = []
        self.set_raw(data)

    def _default_value (self):
        """Returns the default value for this field type. Defined as a
        function so child classes can override default value without
        overriding init.
        """
        return False

    def _validate_field (self, nm, idx, mode):
        """Validation function which notifies update callbacks when the value
        is changed, and sets the status to UNSAVED.
        """
        # If this was triggered from set_raw, do not change the status
        # or the raw
        if self._skip_validation:
            return True
        self.raw = self._boolvar.get()
        self.viewable = self.raw
        self.status = self.STATUS_UNSAVED
        for cb in self._update_callbacks:
            cb()
        return True

    def set_raw (self, raw):
        """Sets the internal raw value, viewable value, and sets the
        checkbox.
        """
        if raw == None:
            raw = self._default_value()
        self.raw = raw
        self.viewable = self.raw
        self._skip_validation = True
        self._boolvar.set(self.viewable)
        self._skip_validation = False

    def register_update_callback (self, cb):
        """Registers a given callback function to be called whenever the field
        text is updated to a valid value by the user.
        """
        self._update_callbacks.append(cb)

    def advance_status (self):
        """Called when the DataEditor is saved. Advances from UNSAVED to SAVED
        and from SAVED to UNTOUCHED.
        """
        if self.status == self.STATUS_UNSAVED:
            self.status = self.STATUS_SAVED
        elif self.status == self.STATUS_SAVED:
            self.status = self.STATUS_UNTOUCHED

    def enable (self, enable):
        """Enables/disables the checkbutton."""
        if enable:
            self.config(state='normal')
        else:
            self.config(state='disabled')

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
    FieldBoolean.test_class(FieldBoolean)
