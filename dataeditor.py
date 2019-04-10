"""dataeditor module
Author = Richard D. Fears
Created = 2017-09-10
Description = Provides the DataEditor Tk widget. This widget provides a
    grid of descriptions and labels for editing a single-level dictionary.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
# Standard Python library imports
import importlib,copy
# My code imports
import helper
from fieldbase import FieldBase
from versionexception import VersionException

class DataEditor (tk.Frame):
    """DataEditor class
    Displays a frame with a grid of labels and text boxes for editing a
    single-level dictionary.
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
        'validation':{
            'untouched':{'bg':'white',},
            'error':{'bg':'red',},
            'unsaved':{'bg':'yellow',},
            'saved':{'bg':'darkgreen',},
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
        # Check for versions which are incompatible with
        # list-of-numbers versions
        try:
            oldtheme['version'] < [0]
        except:
            raise VersionException(
                VersionException.BAD_TYPE,oldtheme['version']
            )

        # If the data version is later than the program version, we will
        # not know how to convert
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
        #    oldtheme['somevariable'] = oldtheme['oldvariable']
        #    oldtheme['version'] = [1,1]

    def __init__ (self, parent, conf, dataeditortheme=None, *args, **options):
        """DataEditor constructor
        Builds a grid of labels and text boxes based on the provided
        configuration. The text boxes can later be
        populated/disabled/enabled/updated by other functions.
        The optional dataeditortheme parameter should be a dict of theming
        preferences. See DEFAULT_THEME for a sample. The leaves of the dict
        tree are Tk config values.
        conf is the important parameter here and has a format similar to
        the following:
        [
            {'type':'string','text':"Title/Ticket",'key':'title','width':20},
            {'type':'string','text':"Description",'key':'description',
                'width':30},
            {'type':'string','text':"Source System",'key':'source system',
                'width':20},
            {'type':'table','text':"Intervals",'key':'intervals',
                'runningdisable':True,'numdatacolumns':4,'columns':[
                    {'type':'datetime','dataindex':0,'text':"Start",
                        'width':19,'runningdisable':True},
                    {'type':'datetime','dataindex':1,'text':"End",
                        'width':19,'runningdisable':True},
                    {'type':'interval','sourceindexes':[0,1],'text':"Length",
                        'width':8,'runningdisable':True},
                    {'type':'boolean','dataindex':2,'text':"Exported",
                        'runningdisable':True},
                    {'type':'string','dataindex':3,'text':"Description",
                        'width':50},
                ]
            },
        ]
        The valid types are string, datetime, boolean, float, integer,
        interval, and table. However, you can extend this by mimicking the
        existing field[type].py modules.
        Example: Create a foo field type by creating a fieldfoo.py module with
        a FieldFoo class which inherits the FieldBase class.
        WARNINGS:
        1) You cannot recursively build tables, as it is unclear what that
           would look like.
        2) Calculated fields (e.g. interval) can only exist within tables and
           the 'sourceindexes' key refers to the column indexes within the
           config, not the raw data.
        3) At the moment, calculated fields *must* be after their source
           columns. In other words, you cannot have
           [datetime,interval[0,2],datetime]. This will hopefully be fixed
           in a future reworking of the DataEditor.
        """
        super().__init__(parent,*args,**options)

        # Initialize internal variables
        # Array of callback functions for when a save occurs
        self._save_callbacks = []
        # Data dict
        self._source_data = None
        # Classes for the field types
        self._field_types = {}

        # Update the dataeditortheme parameters (or set to defaults)
        self._theme = helper.dictVersionUpdate(
            dataeditortheme,
            self._theme_version_update,
            self.DEFAULT_THEME
        )

        # Load the basic types of fields; others will be dynamically loaded
        # as needed
        self._load_basic_field_types()

        # Create the fonts; no need to set anything, as they will be
        # configured in update_theme
        self._labels_font = tkfont.Font()
        self._entries_font = tkfont.Font()
        self._buttons_font = tkfont.Font()
        self._save_button_font = tkfont.Font()
        # Build the labels and entries
        self._original_conf = conf
        self._conf = copy.deepcopy(conf)
        for i,field in enumerate(self._conf):
            field['enabled'] = False
            field['label'] = tk.Label(
                self,text=field['text'],
                font=self._labels_font
            )
            field['label'].grid(column=0,row=i,sticky='ne')
            # One-row fields
            if field['type'] != 'table':
                field['entry'] = self._create_field(self,field)
                if 'width' in field:
                    field['entry'].config(width=field['width'])
                field['entry'].grid(column=1,row=i,sticky='w')
            # Multi-row/column fields
            else:
                field['status'] = FieldBase.STATUS_UNTOUCHED
                field['frame'] = tk.Frame(self)
                field['frame'].grid(column=1,row=i,sticky='w')
                for j,column in enumerate(field['columns']):
                    column['enabled'] = False
                    column['label'] = tk.Label(
                        field['frame'],
                        text=column['text'],
                        font=self._labels_font
                    )
                    column['label'].grid(column=j,row=0,sticky='ew')
                    column['rows'] = []
                    if column['type'] not in self._field_types:
                        self._load_field_type(column['type'])
                field['buttons'] = [] # Don't need buttons until we have data
        # Finally, tack on the save button and revert button
        buttonframe = tk.Frame(self)
        buttonframe.grid(column=0,row=len(self._conf),columnspan=2,sticky='w')
        self._save_button_enabled = False
        self._save_button = tk.Button(
            buttonframe,
            text="Save",
            font=self._save_button_font,
            command=self.save_data
        )
        self._save_button.pack(side='left')
        self._revert_button = tk.Button(
            buttonframe,
            text="Revert",
            font=self._save_button_font,
            command=self.revert_data
        )
        self._revert_button.pack(side='left')

        self.update_theme()

    def _create_field (self, parent, conf, data=None):
        """Checks to make sure the appropriate field module is loaded and
        then constructs one.
        """
        if conf['type'] not in self._field_types:
            self._load_field_type(conf['type'])
        fieldclass = self._field_types[conf['type']]
        newfield = fieldclass(parent,self._entries_font,conf,data)
        newfield.register_update_callback(self._field_updated_callback)
        return newfield

    def _load_basic_field_types (self):
        """Loads the classes for strings, datetimes, booleans, floats,
        and integers.
        """
        for t in ('string','datetime','boolean','float','integer'):
            self._load_field_type(t)

    def _load_field_type (self, fieldtype):
        """Loads the module 'field'+fieldtype and places the class
        'Field'+Fieldtype in the dictionary of field types so that it can
        be used later.
        """
        module = importlib.import_module('field'+fieldtype)
        moduleclass = getattr(module,'Field'+fieldtype.capitalize())
        self._field_types[fieldtype] = moduleclass

    def _field_updated_callback (self):
        """Callback for when a field is updated by the user. Changes any
        SAVED status fields to UNTOUCHED and then updates colors. This is
        so that we get rid of the green when the user starts modifying again.
        """
        for field in self._conf:
            if field['type'] != 'table':
                field['entry'].update_status(
                    FieldBase.STATUS_UNTOUCHED,
                    FieldBase.STATUS_SAVED
                )
            else:
                for column in field['columns']:
                    for cell in column['rows']:
                        cell.update_status(
                            FieldBase.STATUS_UNTOUCHED,
                            FieldBase.STATUS_SAVED
                        )
        self.update_colors()

    def _delete_row (self, field, rowindex):
        """Deletes a row from a table field."""
        for i,column in enumerate(field['columns']):
            cell = column['rows'][rowindex]
            cell.grid_forget()
            del cell
            del column['rows'][rowindex]
        # Also delete the delete button for the row
        button = field['buttons'][rowindex]
        button.grid_forget()
        del button
        del field['buttons'][rowindex]
        # Finally, re-grid so things match up later
        self._regrid(field)
        field['status'] = FieldBase.STATUS_UNSAVED
        self.update_theme()
        # Let other widgets know that the size has changed
        self.event_generate('<<DataEditorChanged>>',when='tail')

    def _add_row (self, field, changestatus=True):
        """Adds a new, defaulted row to the table field."""
        numrows = len(field['columns'][0]['rows'])
        for i,column in enumerate(field['columns']):
            # If this is a raw-data column, let the field constructor
            # use the default
            if 'dataindex' in column:
                entry = self._create_field(field['frame'],column)
            # Otherwise, we need to grab the source fields
            else:
                sources = column['sourceindexes'][:]
                for k in range(len(sources)):
                    sources[k] = field['columns'][sources[k]]['rows'][-1]
                entry = self._create_field(field['frame'],column,sources)
            # Store the entry, size it, and grid it
            column['rows'].append(entry)
            if 'width' in column:
                entry.config(width=column['width'])
            entry.grid(column=i,row=numrows+1,sticky='ew')
        # Also build the new delete button
        button = tk.Button(
            field['frame'],text='-',font=self._buttons_font,
            command=lambda self=self,field=field,rowindex=numrows:
                self._delete_row(field,rowindex)
        )
        field['buttons'].insert(-1,button)
        button.grid(column=len(field['columns'])+1,row=numrows+1)
        # Finally, re-grid so the add button is visible again, and check themes
        self._regrid(field)
        if changestatus:
            field['status'] = FieldBase.STATUS_UNSAVED
        self.update_theme()
        # Let other widgets know that the size has changed
        self.event_generate('<<DataEditorChanged>>',when='tail')

    def _regrid (self, field):
        """Re-grids all cells and buttons in the given table field."""
        for i,column in enumerate(field['columns']):
            for j,cell in enumerate(column['rows']):
                cell.grid(column=i,row=j+1,sticky='ew')
        # Re-grid delete buttons
        numcolumns = len(field['columns'])
        numdelbuttons = len(field['buttons'])-1
        for j in range(numdelbuttons):
            button = field['buttons'][j]
            button.grid(column=numcolumns,row=j+1)
        # Re-grid add button
        field['buttons'][-1].grid(
            column=0,
            row=numdelbuttons+1,
            columnspan=numcolumns+1
        )

    def _update_single_field_color (self, entry):
        """Updates the bg color of the entry based on its status."""
        section = 'validation'
        key = None
        if entry.status == entry.STATUS_UNTOUCHED:
            if issubclass(entry.__class__,tk.Entry) \
                or issubclass(entry.__class__,tk.Text):
                key = 'untouched'
            else:
                section = 'base'
                key = 'widget'
        elif entry.status == entry.STATUS_BADVALUE:
            key = 'error'
        elif entry.status == entry.STATUS_UNSAVED:
            key = 'unsaved'
        elif entry.status == entry.STATUS_SAVED:
            key = 'saved'

        if key != None:
            helper.configThemeFromDict(entry,self._theme,section,key)

    def _build_table (self, field, data):
        """Builds the table of the given field and fills it with the
        given data.
        """
        # Get rid of all existing fields, including buttons
        for column in field['columns']:
            for cell in column['rows']:
                cell.grid_forget()
                del cell
            column['rows'] = []
        for button in field['buttons']:
            button.grid_forget()
            del button
        field['buttons'] = []
        # Now build it back up, by row and then column, so we can eventually
        # have recursive calculated fields.
        # TODO: Actually implement said rec calc fields.
        numcols = field['numdatacolumns']
        for i in range(len(data)):
            for j, column in enumerate(field['columns']):
                # If this is a raw-data column, just feed the data into the
                # constructor
                if 'dataindex' in column:
                    rawdata = data[i][column['dataindex']]
                    entry = self._create_field(field['frame'],column,rawdata)
                # Otherwise, we need to grab the source fields
                else:
                    sources = column['sourceindexes'][:]
                    for k in range(len(sources)):
                        sources[k] = field['columns'][sources[k]]['rows'][i]
                    entry = self._create_field(field['frame'],column,sources)
                # Store the entry, size it, and grid it
                column['rows'].append(entry)
                if 'width' in column:
                    entry.config(width=column['width'])
                entry.grid(column=j,row=i+1,sticky='ew')
            # Create the delete button for this row
            button = tk.Button(
                field['frame'],text='-',font=self._buttons_font,
                command=lambda self=self,field=field,rowindex=i:
                    self._delete_row(field,rowindex)
            )
            field['buttons'].append(button)
            button.grid(column=len(field['columns'])+1,row=i+1)
        # Create the add-row button
        button = tk.Button(
            field['frame'],text='+',font=self._buttons_font,
            command=lambda self=self,field=field:
                self._add_row(field)
        )
        field['buttons'].append(button)
        button.grid(
            column=0,
            row=len(data)+1,
            columnspan=len(field['columns'])+1
        )
        # Finally, update themes
        field['status'] = FieldBase.STATUS_UNTOUCHED
        self.update_theme()

    def _update_single_field_data (self, conf, key, entry,
        column=None, row=None):
        """Updates a given field from the data dict."""
        # If this is a calculated field, just update the calculation
        if 'sourceindexes' in conf:
            entry.calculate_raw_from_sources(automatic=True)
            return
        # If column and row were provided, use those
        if column != None and row != None:
            datacolumn = conf['dataindex']
            entry.set_raw(self._data[key][row][datacolumn])
        # Otherwise, just set from the data dict
        else:
            entry.set_raw(self._data[key])

    ####################
    # Public Functions #
    ####################

    def load_data (self, data):
        """Loads the provided data dict into the fields, building any tables
        in the process.
        """
        self._data = data
        for i,field in enumerate(self._conf):
            if field['key'] not in self._data:
                self._data[field['key']] = ''
            fielddata = self._data[field['key']]

            if field['type'] != 'table':
                field['entry'].set_raw(fielddata)
                field['entry'].status = FieldBase.STATUS_UNTOUCHED
            else:
                self._build_table(field,fielddata)

        self._save_button_enabled = True
        self.update_theme()
        # Let other widgets know that the size has changed
        self.event_generate('<<DataEditorChanged>>',when='tail')

    def save_data (self):
        """Uses the raw values in the entries to fill up the data dict,
        but only for enabled fields. Also handles rebuildng the list-of-lists
        in the data dict that corresponds to tables in the DataEditor.
        """
        # If any fields are in error state, fail immediately
        if self.check_all_field_statuses(FieldBase.STATUS_BADVALUE):
            self.update_colors()
            # TODO: tell the user which ones failed
            return [1]

        for i,field in enumerate(self._conf):
            if field['type'] != 'table':
                # Non-table fields can be ignored outright if they are disabled
                if not field['enabled']:
                    continue
                # If they are enabled, simply set the data value from the raw
                self._data[field['key']] = field['entry'].raw
                field['entry'].advance_status()
            # For tables, we have two different types of enabled
            else:
                # If the main table is enabled, rebuild the list-of-lists
                if field['enabled']:
                    numcols = field['numdatacolumns']
                    numrows = len(field['columns'][0]['rows'])
                    table = [
                        [None for j in range(numcols)] for k in range(numrows)
                    ]
                # Otherwise, use the existing table
                else:
                    table = self._data[field['key']]
                # Go through and update any enabled columns
                for j,column in enumerate(field['columns']):
                    # If the column is raw data and either the column is
                    # enabled or the table was rebuilt, populate this column
                    if column['enabled'] or field['enabled']:
                        for k,cell in enumerate(column['rows']):
                            if 'dataindex' in column:
                                table[k][column['dataindex']] = cell.raw
                            cell.advance_status()
                # Put the table back in place
                self._data[field['key']] = table
                # And advance the table status (for row adds/deletes)
                if field['status'] == FieldBase.STATUS_UNSAVED:
                    field['status'] = FieldBase.STATUS_SAVED
                elif field['status'] == FieldBase.STATUS_SAVED:
                    field['status'] = FieldBase.STATUS_UNTOUCHED
        # Update colors, so the UNSAVED goes to SAVED, etc.
        self.update_colors()
        # Done saving, let the callback functions know (with 0 errors)
        for cb in self._save_callbacks:
            cb([])

    def revert_data (self):
        """Reverts the data to the original state before any user changes."""
        self.load_data(self._data)

    def clear_data (self):
        """Simply sets the internal data dict to None and disables all fields.
        This should be called anytime the underlying data is deleted."""
        self._data = None
        self._save_button_enabled = False
        self.enable_all(False)
        self.update_theme()

    def check_all_field_statuses (self, status=None):
        """Checks all fields for a given status. Returns True if a field has
        that status, False otherwise. If status is not provided, checks for
        UNSAVED or BADVALUE.
        """
        if status == None:
            # Easier to just recursively call this function twice than to
            # have separate logic for a None status
            return self.check_all_field_statuses(FieldBase.STATUS_UNSAVED) \
                or self.check_all_field_statuses(FieldBase.STATUS_BADVALUE)
        for field in self._conf:
            if field['type'] != 'table':
                if field['entry'].status == status:
                    return True
            else:
                for column in field['columns']:
                    for cell in column['rows']:
                        if cell.status == status:
                            return True
        return False

    def register_save_callback (self, function):
        """Registers a function which will be called when the save finishes.
        The function should accept one parameter, a list of error dictionaries.
        Each error dict contains the following keys: label, key, tableindex,
        type, and badtext.
        """
        self._save_callbacks.append(function)

    def update_theme (self):
        """Updates the fonts/colors/styles from the theme attribute. Used when
        the user changes the theme.
        """
        # Update fonts
        helper.configThemeFromDict(
            self._entries_font,self._theme,'fonts','entries'
        )
        helper.configThemeFromDict(
            self._labels_font,self._theme,'fonts','labels'
        )
        helper.configThemeFromDict(
            self._buttons_font,self._theme,'fonts','buttons'
        )
        helper.configThemeFromDict(
            self._save_button_font,self._theme,'fonts','save button'
        )
        # Update widgets
        helper.configThemeFromDict(
            self._save_button,self._theme,'base','save button'
        )
        helper.configThemeFromDict(
            self._revert_button,self._theme,'base','save button'
        )
        for field in self._conf:
            helper.configThemeFromDict(
                field['label'],self._theme,'base','labels'
            )
            if field['type'] != 'table':
                helper.configThemeFromDict(
                    field['entry'],self._theme,'base','entries'
                )
            else:
                for column in field['columns']:
                    helper.configThemeFromDict(
                        column['label'],self._theme,'base','labels'
                    )
                    for cell in column['rows']:
                        helper.configThemeFromDict(
                            cell,self._theme,'base','entries'
                        )
                for button in field['buttons']:
                    helper.configThemeFromDict(
                        button,self._theme,'base','buttons'
                    )
        # Finally update the unchanged/unsaved/errored/etc. font colors and
        # enabled/disabled
        self.update_colors()
        self.update_states()

    def update_colors (self):
        """Called whenever any field changes value, so that the font colors
        can be changed.
        """
        for field in self._conf:
            if field['type'] != 'table':
                self._update_single_field_color(field['entry'])
            else:
                for column in field['columns']:
                    # For tables, we can also mark the frame background if we
                    # added/deleted a row
                    if field['status'] == FieldBase.STATUS_UNTOUCHED:
                        helper.configThemeFromDict(
                            field['frame'],self._theme,'base','widget')
                    elif field['status'] == FieldBase.STATUS_UNSAVED:
                        helper.configThemeFromDict(
                            field['frame'],self._theme,'validation','unsaved')
                    elif field['status'] == FieldBase.STATUS_SAVED:
                        helper.configThemeFromDict(
                            field['frame'],self._theme,'validation','saved')
                    # Color all the cells appropriately
                    for cell in column['rows']:
                        self._update_single_field_color(cell)

    def update_data_running (self):
        """Updates the data from the data dict for all disabled keys."""
        if self._data == None:
            return
        for field in self._conf:
            if field['type'] != 'table':
                if 'runningdisable' in field and field['runningdisable']:
                    self._update_single_field_data(
                        field,field['key'],field['entry']
                    )
            else:
                # If the number of rows in the data differs from the number
                # of rows in the DataEditor table, the most likely cause is
                # that the user just started a new timer interval.
                # In that case, we just want to add a new row.
                if len(self._data[field['key']]) \
                        == len(field['columns'][0]['rows']) + 1:
                    self._add_row(field,changestatus=False)
                    row = len(field['columns'][0]['rows'])-1
                    for j,column in enumerate(field['columns']):
                        cell = column['rows'][row]
                        self._update_single_field_data(
                            column,field['key'],cell,j,row
                        )
                # If the row counts differ, but by more than 1, we need
                # to rebuild (potentially losing unsaved data)
                elif len(self._data[field['key']]) \
                        != len(field['columns'][0]['rows']):
                    self._build_table(field,self._data[field['key']])
                # Finally, if the row counts match, just update the
                # disabled columns
                else:
                    for j,column in enumerate(field['columns']):
                        if 'runningdisable' in column \
                                and column['runningdisable']:
                            for k,cell in enumerate(column['rows']):
                                self._update_single_field_data(
                                    column,field['key'],cell,j,k
                                )

    def enable_all (self, enable=True):
        """Enables/disables all fields and buttons."""
        for field in self._conf:
            field['enabled'] = enable
            if field['type'] == 'table':
                for column in field['columns']:
                    column['enabled'] = enable
        self.update_states()

    def disable_for_running (self):
        """Disables all fields/columns which are marked for disabling while
        a timer is running.
        """
        for field in self._conf:
            if 'runningdisable' in field and field['runningdisable']:
                field['enabled'] = False
            if field['type'] == 'table':
                for column in field['columns']:
                    if 'runningdisable' in column and column['runningdisable']:
                        column['enabled'] = False
        self.update_states()

    def update_states (self):
        """Enables/disables the entry fields according to the 'enabled' key
        in each field.
        """
        for field in self._conf:
            if field['type'] != 'table':
                field['entry'].enable(field['enabled'])
            else:
                for column in field['columns']:
                    for cell in column['rows']:
                        cell.enable(column['enabled'])
                for button in field['buttons']:
                    if field['enabled']:
                        button.config(state='normal')
                    else:
                        button.config(state='disabled')
        if self._save_button_enabled:
            self._save_button.config(state='normal')
            self._revert_button.config(state='normal')
        else:
            self._save_button.config(state='disabled')
            self._revert_button.config(state='disabled')

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
            {'type':'string','text':"Title/Ticket",'key':'title',
                'width':20},
            {'type':'string','text':"Description",'key':'description',
                'width':30},
            {'type':'string','text':"Source System",'key':'source system',
                'width':20},
            {'type':'table','text':"Intervals",'key':'intervals',
                'numdatacolumns':4,'columns':[
                    {'type':'datetime','dataindex':0,'text':"Start",
                        'width':19},
                    {'type':'datetime','dataindex':1,'text':"End",
                        'width':19},
                    {'type':'interval','sourceindexes':[0,1],'text':"Length",
                        'width':8},
                    {'type':'boolean','dataindex':2,'text':"Exported"},
                    {'type':'string','dataindex':3,'text':"Description",
                        'width':50},
            ]},
        ]
        data = {
            "description":"Default timer",
            "title":"TIMER",
            "version":[1,0,0],
            "source system":"YATTi", "intervals":[
                [1505221371.8944616,1505221375.320189,False,""],
                [1505222275.3718667,1505222283.2568984,False,""]
            ],
        }
        de = DataEditor(root,config)
        de.pack()
        de.register_save_callback(save_callback)
        de.load_data(data)
        de.enable_all()
        label = tk.Label(root,text=" ")
        label.pack()
        root.mainloop()
    except Exception as e:
        print()
        traceback.print_exc()
    finally:
        input("Press enter to quit")


