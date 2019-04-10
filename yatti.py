"""yatti module
Author = Richard D. Fears
Created = 2017-08-25
Description = Main file of the YATTi program. Builds and displays all of the
    necessary screens (e.g. timers, calendar, timer data). Also reads and
    writes out the theme, data, settings, and password files.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
import tkinter.messagebox as tkmessagebox
# Standard Python library imports
import os, sys, json, base64, time, platform, math
from appdirs import AppDirs
# My code imports
import helper
from timerbutton import TimerButton
from dataeditor import DataEditor
from csvexport import CSVExport

class YattiMain:
    """YattiMain class
    Driver class for the YATTi program.
    """

    # DO NOT CHANGE THE DEFAULTS BELOW!
    # If you want to change your personal theme, edit 'default-theme.json'.
    # If you want to change your settings, edit settings.json.
    OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
    DEFAULT_THEME = {
        'version':[1,0,0],
        'calendar':{},
        'timerbuttons':{},
        'dataeditor':{},
        'csvexport':{},
        'base':{
            'buttons':{},
        },
        'fonts':{
            'buttons':{'size':20,},
        },
    }
    OLDEST_CONVERTIBLE_SETTINGS_VERSION = [1,0,0]
    DEFAULT_SETTINGS = {
        'version':[1,0,0],
        'timerbuttons':{},
        'csvexport':{},
        'root width':1200,
        'root height':800,
        'pause other timers':True,
        'theme file':'default-theme.json',
        'data file':'timerdata.json',
        'passwords file':'passwords.bin',
        'connection info':{
            'jira':{
                'site':'',
                'username':'',
                'save password':'',
            },
            'openair':{
                'site':'',
                'username':'',
                'save password':'',
            },
            'trac':{
                'site':'',
                'username':'',
                'save password':'',
            },
        },
    }
    OLDEST_CONVERTIBLE_DATA_VERSION = [1,0,0]
    DEFAULT_DATA = {
        'version':[1,0,0],
        'timerdata':[],
    }
    DATA_CONFIG = [
        {'type':'string','text':"Title/Ticket",'key':'title',
            'width':20},
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
    OLDEST_CONVERTIBLE_PASSWORDS_VERSION = [1,0,0]
    DEFAULT_PASSWORDS = {
        'version':[1,0,0],
        'jira':'',
        'openair':'',
        'trac':'',
    }

    def _settings_version_update (self, oldsettings):
        """_settings_version_update internal function
        Updates the old settings to the new format, based on relative versions.
        """
        # Check for versions which are incompatible with
        # list-of-numbers versions
        try:
            oldsettings['version'] < [0]
        except:
            raise VersionException(
                VersionException.BAD_TYPE,oldsettings['version']
            )

        # If the settings version is later than the program version, we will
        # not know how to convert
        if oldsettings['version'] > YattiMain.DEFAULT_SETTINGS['version']:
            raise VersionException(VersionException.TOO_NEW,
                oldsettings['version'],YattiMain.DEFAULT_SETTINGS['version'])

        # If the old version is too old, we will not know how to convert
        if oldsettings['version'] \
                < YattiMain.OLDEST_CONVERTIBLE_SETTINGS_VERSION:
            raise VersionException(
                VersionException.TOO_OLD,
                oldsettings['version'],
                YattiMain.DEFAULT_SETTINGS['version']
            )

        # Finally, convert incrementally through all the versions
        # Below is some sample code to copy:
        #if oldsettings['version'] < [1,1]:
        #    oldsettings['somevariable'] = oldsettings['oldvariable']
        #    oldsettings['version'] = [1,1]

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

        # If the theme version is later than the program version, we will
        # not know how to convert
        if oldtheme['version'] > YattiMain.DEFAULT_THEME['version']:
            raise VersionException(VersionException.TOO_NEW,
                oldtheme['version'],YattiMain.DEFAULT_THEME['version'])

        # If the old version is too old, we will not know how to convert
        if oldtheme['version'] < YattiMain.OLDEST_CONVERTIBLE_THEME_VERSION:
            raise VersionException(VersionException.TOO_OLD,
                oldtheme['version'],YattiMain.DEFAULT_THEME['version'])

        # Finally, convert incrementally through all the versions
        # Below is some sample code to copy:
        #if oldtheme['version'] < [1,1]:
        #    oldtheme['somevariable'] = oldtheme['oldvariable']
        #    oldtheme['version'] = [1,1]

    def _passwords_version_update (self, oldpasswords):
        """_passwords_version_update internal function
        Updates the old passwords to the new format, based on relative
        versions.
        """
        # Check for versions which are incompatible with
        # list-of-numbers versions
        try:
            oldpasswords['version'] < [0]
        except:
            raise VersionException(
                VersionException.BAD_TYPE,oldpasswords['version']
            )

        # If the passwords version is later than the program version,
        # we will not know how to convert
        if oldpasswords['version'] > YattiMain.DEFAULT_PASSWORDS['version']:
            raise VersionException(VersionException.TOO_NEW,
                oldpasswords['version'],YattiMain.DEFAULT_PASSWORDS['version'])

        # If the old version is too old, we will not know how to convert
        if oldpasswords['version'] \
                < YattiMain.OLDEST_CONVERTIBLE_PASSWORDS_VERSION:
            raise VersionException(VersionException.TOO_OLD,
                oldpasswords['version'],YattiMain.DEFAULT_PASSWORDS['version'])

        # Finally, convert incrementally through all the versions
        # Below is some sample code to copy:
        #if oldpasswords['version'] < [1,1]:
        #    oldpasswords['somevariable'] = oldpasswords['oldvariable']
        #    oldpasswords['version'] = [1,1]

    def _data_version_update (self, olddata):
        """_data_version_update internal function
        Updates the old data to the new format, based on relative versions.
        """
        # Check for versions which are incompatible with
        # list-of-numbers versions
        try:
            olddata['version'] < [0]
        except:
            raise VersionException(
                VersionException.BAD_TYPE,olddata['version']
            )

        # If the data version is later than the program version, we will
        # not know how to convert
        if olddata['version'] > YattiMain.DEFAULT_DATA['version']:
            raise VersionException(VersionException.TOO_NEW,
                olddata['version'],YattiMain.DEFAULT_DATA['version'])

        # If the old version is too old, we will not know how to convert
        if olddata['version'] < YattiMain.OLDEST_CONVERTIBLE_DATA_VERSION:
            raise VersionException(VersionException.TOO_OLD,
                olddata['version'],YattiMain.DEFAULT_DATA['version'])

        # Finally, convert incrementally through all the versions
        # Below is some sample code to copy:
        #if olddata['version'] < [1,1]:
        #    olddata['somevariable'] = olddata['oldvariable']
        #    olddata['version'] = [1,1]

    def __init__ (self):
        """YattiMain constructor
        Reads in the default theme, data, settings, and password files.
        If any of them do not exist yet, it creates base versions.
        """
        # Get the preferred settings location
        global DEBUG
        try:
            DEBUG
        except:
            DEBUG = False
        if DEBUG:
            self._dirs = AppDirs(
                appname="YATTi",
                appauthor="GrayShadowSoftware",
                version="Debug"
            )
        else:
            self._dirs = AppDirs(
                appname="YATTi",
                appauthor="GrayShadowSoftware"
            )
        configprefix = self._dirs.user_config_dir
        dataprefix = self._dirs.user_data_dir
        # Get the current OS (may need to modify this later)
        self._running_os = platform.system()
        # First read in the settings file
        self._settingsfilename = "settings.json"
        self._settings = self._load_file_or_defaults("settings",
            configprefix+os.sep+self._settingsfilename,
            self._settings_version_update,self.DEFAULT_SETTINGS)
        # The settings file will contain the rest of the filenames
        self._theme = self._load_file_or_defaults("theme",
            configprefix+os.sep+self._settings['theme file'],
            self._theme_version_update,self.DEFAULT_THEME)
        self._data = self._load_file_or_defaults("data",
            dataprefix+os.sep+self._settings['data file'],
            self._data_version_update,self.DEFAULT_DATA)
        self._passwords = self._load_file_or_defaults("passwords",
            configprefix+os.sep+self._settings['passwords file'],
            self._passwords_version_update,
            self.DEFAULT_PASSWORDS,self._decrypt_password_file)

    def _decrypt_password_file (self, filetext):
        """_decrypt_password_file internal function
        Takes raw text from an encrypted file and converts it to decrypted JSON
        text string.
        TODO: Currently just returns the filetext. Need to actually add
        decryption logic.
        """
        return filetext

    def _encrypt_password_file (self, jsontext):
        """_encrypt_password_file internal function
        Takes a JSON text string and converts it to an encrypted string for
        writing to a file.
        TODO: Currently just returns the jsontext. Need to actually add
        encryption logic.
        """
        return jsontext

    def _load_file_or_defaults (self, dictname, filename, updatefunc,
            defaults, wrapperfunc = None):
        """_load_file_or_defaults internal function
        Reads JSON from a file if it exists. If it doesn't, loads from
        defaults. In either case, it returns the resulting dict.
        """
        # Try to read in the JSON file
        try:
            with open(filename) as fileobj:
                if wrapperfunc == None:
                    thedict = json.load(fileobj)
                else:
                    thedict = json.loads(wrapperfunc(fileobj.read()))
        # If we can't, default to a basic dict
        # TODO: Switch to debug log
        except:
            print("No "+filename+" file found. Creating default "+dictname+".",
                file=sys.stderr)
            thedict = {}
        # We've either read in and interpreted a JSON dict, or created a base
        # one. Now make sure to update it/fill it with defaults.
        thedict = helper.dictVersionUpdate(thedict,updatefunc,defaults)
        return thedict

    def _timerframecanvas_reconfigure (self):
        """Reconfigures the timer list's canvas's scrollregion and width when
        its view is reconfigured.
        """
        # Only reconfigure the canvas if it's already been rendered
        if not self._timerframecanvas.winfo_viewable():
            self._timerframecanvas.after(20,self._timerframecanvas_reconfigure)
            return
        self._timerframecanvas.config(
            scrollregion=self._timerframecanvas.bbox('all'),
            width=self._timerframe.winfo_width()
        )

    def _dataeditorcanvas_reconfigure (self):
        """Reconfigures the data editor's canvas's scrollregion and width when
        its view is reconfigured.
        """
        # Only reconfigure the canvas if it's already been rendered
        if not self._dataeditorcanvas.winfo_viewable():
            self._dataeditorcanvas.after(20,self._dataeditorcanvas_reconfigure)
            return
        self._dataeditor.update_idletasks()
        self._dataeditorcanvas.config(
            scrollregion=self._dataeditorcanvas.bbox('all')
        )

    def run (self):
        """run function
        Main driver function for YATTi program. Builds all the widgets and runs
        the main loop.
        """
        self._root = tk.Tk()
        self._root.title("YATTi - Yet Another Tracker of Time")
        self._root.protocol("WM_DELETE_WINDOW",self._close_window)
        #self._root.iconbitmap("YATTi.ico")
        # Grab the previous size from the settings and place the window in the
        # center of the screen
        rootwidth = self._settings['root width']
        rootheight = self._settings['root height']
        screenwidth = self._root.winfo_screenwidth()
        screenheight = self._root.winfo_screenheight()
        xpos = (screenwidth/2)-(rootwidth/2)
        ypos = (screenheight/2)-(rootheight/2)
        self._root.geometry('%dx%d+%d+%d'%(rootwidth,rootheight,xpos,ypos))
        # Right pane column and timer list row should expand when
        # window resized
        self._root.grid_columnconfigure(2,weight=1)
        self._root.grid_rowconfigure(1,weight=1)
        self._timers = []
        ### Menu ###
        menubar = tk.Menu(self._root)
        self._root.config(menu=menubar)
        # File menu
        filemenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File",underline=0,menu=filemenu)
        filemenu.add_command(label="Save",underline=0,
            command=self._write_all_files)
        # Timer menu
        timermenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Timers",underline=0,menu=timermenu)
        timermenu.add_command(label="Add New Timer",underline=0,
            command=self._add_timer)
        timermenu.add_separator()
        timermenu.add_command(label="Sort Timers by Title",underline=0,
            command=self._sort_timers_title)
        timermenu.add_command(label="Archive Exported Time Slices",underline=8,
            command=self._archive_intervals)
        timermenu.add_command(label="Archive Selected Timer",underline=10,
            command=self._archive_selected_timer)
        # Export menu
        exportmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Export",underline=1,menu=exportmenu)
        exportmenu.add_command(label="Export to CSV",underline=10,
            command=self._export_to_csv)
        # Options menu
        optionsmenu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="Options",underline=0,menu=optionsmenu)
        self._pause_other_timers_var = tk.BooleanVar()
        self._pause_other_timers_var.set(self._settings['pause other timers'])
        optionsmenu.add_checkbutton(
            label="Pause other timers when timer started",underline=0,
            command=lambda self=self,target='pause other timers': \
                           self._options_toggle(target),
            variable=self._pause_other_timers_var
        )
        ### Left pane ###
        # Timer button frame
        self._timerframeouter = tk.Frame(self._root)
        self._timerframeouter.grid(column=1,row=1,sticky='ns')
        self._timerframecanvas = tk.Canvas(self._timerframeouter)
        self._timerframe = tk.Frame(self._timerframecanvas)
        self._timerframe.pack(fill='both',expand=True)
        timerscrollbar = tk.Scrollbar(self._timerframeouter,orient='vertical',
            command=self._timerframecanvas.yview)
        self._timerframecanvas.config(yscrollcommand=timerscrollbar.set)
        timerscrollbar.pack(side='right',fill='y',expand=True)
        self._timerframecanvas.pack(side='left',fill='y',expand=True)
        self._timerframecanvas.create_window(
            (0,0),window=self._timerframe,anchor='nw'
        )
        self._timerframe.bind(
            '<Configure>',
            lambda e,self=self: self._timerframecanvas_reconfigure
        )
        # Add quick-add button
        self._button_font = tkfont.Font()
        self._quick_add_button = tk.Button(self._root,font=self._button_font,
            text="Quick-Add Timer",command=self._add_timer)
        self._quick_add_button.grid(column=1,row=2)
        tempbutton = tk.Button(
            self._root,text="Test",
            command=lambda self=self: \
                           self._dataeditor.event_generate('<Configure>')
        )
        tempbutton.grid(column=1,row=3)

        ### Right pane ###
        ### Data Editor ###
        self._current_timerbutton = None
        self._dataeditor_updater = None
        self._dataeditorframe = tk.Frame(self._root)
        self._dataeditorframe.grid(row=1,column=2,rowspan=2,sticky='nsew')
        self._dataeditorframe.grid_columnconfigure(0,weight=1)
        self._dataeditorframe.grid_rowconfigure(0,weight=1)
        self._dataeditorcanvas = tk.Canvas(self._dataeditorframe)
        self._dataeditor = DataEditor(self._dataeditorcanvas,self.DATA_CONFIG,
            self._theme['dataeditor'])
        self._dataeditor.pack()
        self._dataeditor.register_save_callback(self._data_editor_saved)
        # Scrollbars
        dataeditorvertscrollbar = tk.Scrollbar(
            self._dataeditorframe,
            orient='vertical',
            command=self._dataeditorcanvas.yview
        )
        dataeditorvertscrollbar.grid(row=0,column=1,sticky='ns')
        dataeditorhorzscrollbar = tk.Scrollbar(
            self._dataeditorframe,
            orient='horizontal',
            command=self._dataeditorcanvas.xview
        )
        dataeditorhorzscrollbar.grid(row=1,column=0,sticky='ew')
        self._dataeditorcanvas.config(
            yscrollcommand=dataeditorvertscrollbar.set,
            xscrollcommand=dataeditorhorzscrollbar.set
        )
        # Pack it up
        self._dataeditorcanvas.grid(row=0,column=0,sticky='nsew')
        self._dataeditorcanvas.create_window(
            (0,0),window=self._dataeditor,anchor='nw'
        )
        self._dataeditor.bind('<Configure>',
            lambda e,self=self: self._dataeditorcanvas_reconfigure())

        ### Scrollwheel enablement ###
        if self._running_os in ("Windows","Darwin"):
            self._root.bind_all("<MouseWheel>",self._mousewheel_callback)
        elif self._running_os == "Linux":
            self._root.bind_all("<Button-4>",self._mousewheel_callback)
            self._root.bind_all("<Button-5>",self._mousewheel_callback)

        ### Adding timer buttons and reconfiguring ###
        self._load_timers_from_json()
        self.update_theme()

        self._root.mainloop()

    def _close_window (self):
        """_close_window internal function
        Callback for when the main window is closed. Saves all files and then
        exits.
        """
        # Kill all running timers
        for timer in self._timers:
            timer.running = False
        if self._dataeditor_updater != None:
            self._root.after_cancel(self._dataeditor_updater)
            self._dataeditor_updater = None
        # By default, always save results
        self._write_all_files()
        # Die, die, die!
        self._root.destroy()

    def _set_current_timerbutton (self, tb):
        """_set_current_timerbutton internal function
        Called when clicking on a timer label. Initializes the data editor's
        data.
        """
        self._current_timerbutton = tb
        self._dataeditor.load_data(self._current_timerbutton._data)
        self._dataeditor.enable_all()
        self._dataeditorcanvas_reconfigure()

        if self._dataeditor_updater != None:
            self._root.after_cancel(self._dataeditor_updater)
            self._dataeditor_updater = None
        if self._current_timerbutton.running:
            self._dataeditor_updater = self._root.after(
                500,self._update_dataeditor)
            # Disable the intervals table
            self._dataeditor.disable_for_running()

    def _options_toggle (self, target):
        """_options_toggle internal function
        Handles toggling an option from the Options menu. target is a string
        identifying which checkbox got checked.
        """
        if target == 'pause other timers':
            self._settings['pause other timers'] = \
                self._pause_other_timers_var.get()

    def _update_dataeditor (self):
        """_update_dataeditor internal function
        Updates the intervals section of the data editor, allowing a running
        timer.
        """
        self._dataeditor.update_data_running()
        self._dataeditor_updater = self._root.after(
            500,self._update_dataeditor)

    def _data_editor_saved (self, errors):
        """_data_editor_saved callback function
        Called when the data editor save button is clicked. Updates the timer
        button data.
        """
        if self._current_timerbutton == None:
            return
        self._current_timerbutton.update_data()

    def _mousewheel_callback (self, e):
        """_mousewheel_callback callback function
        Called when the mousewheel is scrolled anywhere. Uses winfo to figure
        out which widget currently holds the pointer focus and then uses Tk's
        "parent as a substring of child" naming convention.
        """
        x,y = self._root.winfo_pointerxy()
        widget = self._root.winfo_containing(x,y)
        try:
            str(widget).index(str(self._timerframeouter))
            isovercanvas = True
        except:
            isovercanvas = False

        if isovercanvas:
            if self._running_os == "Windows":
                scrolldir = -1 if e.delta<0 else 1
                scrollby = -1*math.ceil(abs(e.delta)/120)
            elif self._running_os == "Darwin":
                scrolldir = -1 if e.delta<0 else 1
                scrollby = -1*abs(e.delta)
            elif self._running_os == "Linux":
                scrolldir = -1 if e.delta<0 else 1
                scrollby = -1*math.ceil(abs(e.delta)/120)
            self._timercanvas.yview_scroll(scrolldir*scrollby,'units')

    def _write_all_files (self):
        """_write_all_files internal function
        Writes the settings, theme, data, and passwords dictionaries to their
        respective files.
        """
        self._write_file("settings",self._settings,self._dirs.user_config_dir,
            self._settingsfilename)
        self._write_file("theme",self._theme,self._dirs.user_config_dir,
            self._settings['theme file'])
        self._write_file("data",self._data,self._dirs.user_data_dir,
            self._settings['data file'])
        self._write_file("passwords",self._passwords,
            self._dirs.user_config_dir,
            self._settings['passwords file'],self._encrypt_password_file)

    def _write_file (self, dictname, sourcedict, filedir, filename,
            wrapperfunc = None):
        """_write_file internal function
        Writes the given sourcedict as JSON to the given filename, optionally
        running wrapperfunc on the JSON first.
        """
        # Create the directory
        if not os.path.exists(filedir):
            os.makedirs(filedir)
        # Try to write out the JSON
        try:
            with open(filedir+os.sep+filename,'w') as fileobj:
                if wrapperfunc == None:
                    json.dump(
                        sourcedict,fileobj,indent="\t",separators=(', ',':')
                    )
                else:
                    fileobj.write(
                        wrapperfunc(
                            json.dumps(
                                sourcedict,
                                indent="\t",
                                separators=(', ',':')
                            )
                        )
                    )
            return True
        # If we can't, notify the user
        # TODO: Switch to debug file
        except:
            print(dictname+" JSON could not be written to " \
                +(filedir+os.sep+filename)+".",
                file=sys.stderr
            )
            traceback.print_exc()
            return False

    def _load_timers_from_json (self):
        """_load_timers_from_json internal function
        Adds all the timers found in the JSON file that was read in at the
        start of the program.
        """
        for data in self._data['timerdata']:
            self._add_timer(data)

    def _export_to_csv (self):
        """_export_to_csv internal function
        Sets up and runs the CSV export class to export current data to CSV.
        """
        exportwindow = CSVExport(self._root,self._data,
            self._settings['csvexport'],self._theme['csvexport'])
        self._root.wait_window(exportwindow)
        for timer in self._timers:
            timer.update_data()
        self._dataeditor.clear_data()

    def _add_timer (self, timerdata=None):
        """_add_timer internal function
        Adds a timer button to the list. timerdata can be specified if loading
        an existing timer.
        """
        if timerdata == None:
            self._data['timerdata'].append({})
            timerdata = self._data['timerdata'][-1]
        self._timers.append(
            TimerButton(
                self._timerframe,
                timerdata,
                self._settings['timerbuttons'],
                self._theme['timerbuttons']
            )
        )
        self._timers[-1].pack()
        self._timers[-1].register_toggle_callback(self._timer_toggled)
        self._timers[-1].register_labelclick_callback(
            self._set_current_timerbutton
        )
        self._timers[-1].register_startqual_callback(self._start_allowed)
        self._timerframecanvas_reconfigure()
        self._timerframecanvas.yview_moveto(1)

    def _sort_timers_title (self):
        """_sort_timers_title internal function
        Sorts the timer list by the titles of the timers and then reload the
        list.
        """
        self._data['timerdata'].sort(key=lambda i: i['title'])
        self._reload_timers()

    def _reload_timers (self):
        """_reload_timers internal function
        Removes and then readds all of the timerbuttons. Remembers running
        timers and selected timer. Used whenever timers are removed or change
        order in the data.
        """
        # Remember which timers were selected/running.
        current_timer_data = None
        running_timers = []
        if self._current_timerbutton != None:
            current_timer_data = self._current_timerbutton._data
            self._current_timerbutton = None
        for timer in self._timers:
            if timer.running:
                running_timers.append(timer._data)
                timer.running = False
        # Remove all the old timer buttons and re-add in sorted order.
        for timer in self._timers:
            timer.destroy()
        self._timers = []
        self._load_timers_from_json()
        # Restart any running timers
        for timer in self._timers:
            if timer._data in running_timers:
                timer.running = True
        # Reselect the previously selected timer
        for timer in self._timers:
            if timer._data == current_timer_data:
                self._current_timerbutton = timer
                # Also check if the selected timer is running; if so, run the
                # logic for such
                if timer._data in running_timers:
                    self._timer_toggled(timer)

    def _archive_intervals (self):
        """_archive_intervals callback function
        Wrapper function which calls _archive_timer_intervals for each timer in
        the data.
        """
        self._dataeditor.clear_data()
        numexported = 0
        error = False
        failedtimers = []
        for timer in self._timers:
            returnval = self._archive_timer_intervals(timer)
            if returnval >= 0:
                numexported += returnval
            else:
                error = True
                failedtimers.append(timer)
        if error:
            tkmessagebox.showerror(title="Failed to Archive",
                message=("Failed to archive intervals for {} timers.\n"+ \
                    "Successfully archived {} intervals from {} timers."
                ).format(
                    len(failedtimers),
                    numexported,
                    len(self._timers)-len(failedtimers)
                )
            )
        else:
            tkmessagebox.showinfo(title="Archived Successfully",
                message=("Successfully archived {} intervals from {} timers."
                ).format(
                    numexported,
                    len(self._timers)-len(failedtimers)
                )
            )

    def _archive_timer_intervals (self, timer, exportedonly=True):
        """_archive_timer_intervals internal function
        Removes intervals from a timer and puts them in separate "archive"
        files. If exportedonly is False, unexported time will also be archived.
        """
        timerdata = timer._data
        filename = "YATTi_archive_"+timerdata['title']+".json"
        filedir = self._dirs.user_data_dir
        # First try to read in the file, in case there's any existing data
        archivedata = {}
        try:
            with open(filedir+os.sep+filename,'r') as f:
                archivedata = json.load(f)
        except:
            # TODO: log some debug data
            pass
        # Fill in the timer details (we don't care about version)
        archivedata['title'] = timerdata['title']
        archivedata['description'] = timerdata['description']
        archivedata['source system'] = timerdata['source system']
        # Gather the intervals we want to export
        exportintervals = []
        for interval in timerdata['intervals']:
            if interval[2] or not exportedonly:
                exportintervals.append(interval)
        # Next, merge any existing data and our current timer data
        if 'intervals' in archivedata \
                and type(archivedata['intervals']) == type([]):
            archivedata['intervals'] += exportintervals
        else:
            archivedata['intervals'] = exportintervals
        # Finally, try to write it out
        if self._write_file("Archive",archivedata,filedir,filename):
            # If we succeeded in writing the intervals out, remove them from
            # current data and then update the timer (and possibly the
            # data editor)
            for interval in exportintervals:
                timerdata['intervals'].remove(interval)
            timer.update_data()
            return len(exportintervals)
        else:
            return -1

    def _archive_selected_timer (self):
        """_archive_selected_timer callback function
        Archives all intervals for the currently-selected timer and then
        removes the whole timer from the list of timers.
        """
        timer = self._current_timerbutton
        if timer == None:
            return
        # Shut down any related afters
        if timer.running:
            timer.running = False
        if self._dataeditor_updater != None:
            self._root.after_cancel(self._dataeditor_updater)
            self._dataeditor_updater = None
        self._dataeditor.enable_all(False)
        # Archive all intervals
        success = self._archive_timer_intervals(timer,exportedonly=False)
        if success == -1:
            tkmessagebox.showerror(title="Failed to Archive Intervals",
                message="Intervals for selected timer could not be " + \
                        "archived.\nTimer will not be removed."
            )
            return
        # Intervals were successfully removed; update data editor and then
        # disable it
        self._dataeditor.clear_data()
        # Remove the timer completely
        self._data['timerdata'].remove(timer._data)
        timer.pack_forget()
        timer.destroy()
        self._timers.remove(timer)
        self._current_timerbutton = None
        # Notify the user
        tkmessagebox.showinfo(title="Timer Successfully Archived",
            message="Timer successfully archived. {} intervals archived." \
                    .format(success)
        )

    def _timer_toggled (self, thetimer):
        """_timer_toggled callback function
        The function which is called for each timer when said timer is toggled.
        """
        # If we want to pause other timers when this one is started, do so
        if self._settings['pause other timers'] and thetimer.running:
            for timer in self._timers:
                if timer != thetimer:
                    timer.running = False
        # Select the timer if we just started it
        if thetimer.running:
            self._set_current_timerbutton(thetimer)
            if self._current_timerbutton.running:
                self._dataeditor_updater = self._root.after(
                    500,self._update_dataeditor)
        # If the timer is not running, but is selected anyways, enable editing
        elif thetimer == self._current_timerbutton:
            self._dataeditor.enable_all()
            # If there is a running dataeditor updater, cancel it
            if self._dataeditor_updater != None:
                self._root.after_cancel(self._dataeditor_updater)
                self._dataeditor_updater = None

    def _start_allowed (self, timer):
        """Callback function to determine if the timer button is allowed to
        actually start.
        """
        # Check if the data editor is initialized and has unsaved updates
        if self._dataeditor.check_all_field_statuses():
            return False
        return True

    def update_theme (self):
        """update_theme function
        Updates the fonts/colors/styles from the theme attribute. Used when
        the user changes the theme.
        """
        widgets = (
            (self._quick_add_button,'basic'),
            (self._root,'widget'),
            (self._quick_add_button,'buttons'),
        )
        fontwidgets = (
            (self._button_font,'buttons'),
        )
        subwidgets = [self._dataeditor]+self._timers

        for widget,name in widgets:
            helper.configThemeFromDict(widget,self._theme,'base',name)
        for widget,name in fontwidgets:
            helper.configThemeFromDict(widget,self._theme,'fonts',name)
        for widget in subwidgets:
            widget.update_theme()


if __name__ == "__main__":
    import os, sys, traceback
    # cd to the script directory
    try:
        if getattr(sys,'frozen',False):
            # The app is frozen, so get the dir of the executable
            os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
        else:
            # The app is not frozen, so we should use the location of the
            # script file
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
    except Exception as e:
        print("No execute access to script directory")
        raise
    # Check if we were passed the debug flag
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        DEBUG = True
    else:
        DEBUG = False

    try:
        main = YattiMain()
        main.run()
    except Exception as e:
        print()
        traceback.print_exc()
    finally:
        # If the app is not frozen, pause the console window so we can
        # see errors
        if not getattr(sys,'frozen',False):
            input("Press enter to quit")

