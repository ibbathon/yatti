"""csvexport module
Author = Richard D. Fears
Created = 2017-09-19
Description = Provides the CSVExport Tk widget, which provides several options
    for customizing a CSV export.
"""
# Tk imports
import tkinter as tk
import tkinter.font as tkfont
import tkinter.filedialog as tkfiledialog
import tkinter.messagebox as tkmessagebox
# Standard Python library imports
import time, traceback
# My code imports
import helper
from versionexception import VersionException

class CSVExport (tk.Toplevel):
    """CSVExport class
    Displays a toplevel widget with various checkboxes, radio buttons, and
    other options for customizing the CSV export for a set of data.
    """

    OLDEST_CONVERTIBLE_SETTINGS_VERSION = [1,0,0]
    DEFAULT_SETTINGS = {
        'version':[1,0,0],
        'filename':'YATTi-export-{timestamp}-{fullsummary}.csv',
        'filepath':'',
        'filepath width':100,
        'export all slices':False,
        'mark as exported':True,
        'export full rows':True,
        'export summary rows':True,
        'time formats':{
            'date':'%Y-%m-%d',
            'time':'%H:%M',
            'duration':{
                'roundingamount':0.25,
                # Available values are rawhours, inthours, intminutes,
                # and roundedhours
                'full':'{inthours}h {intminutes}m',
                'summary':'{roundedhours}',
            },
        },
        'column descriptions':{
            'type':"slice or summary",
            'source':"ticket source",
            'previousexport':"whether or not the slice has been previously" \
                + " exported (blank for summary rows)",
            'title':"ticket title",
            'description':"ticket description",
            'startdate':"date portion of slice start time (YYYY-mm-dd)",
            'starttime':"time portion of slice start time (HH:MM)" \
                + " (blank for summary rows)",
            'endtime':"time portion of slice end time (HH:MM)" \
                + " (blank for summary rows)",
            'duration':"time spent on slice (in correct format for" \
                + " full/summary)",
            'task':"slice description",
        },
        'column names':{
            'type':"Full/Summary",
            'source':"Source",
            'previousexport':"Already Exported?",
            'title':"Ticket Title",
            'description':"Ticket Description",
            'startdate':"Work Date",
            'starttime':"Start Time",
            'endtime':"End Time",
            'duration':"Duration",
            'task':"Work Description",
        },
        'export columns':[
            'type',
            'source',
            'previousexport',
            'title',
            'description',
            'startdate',
            'starttime',
            'endtime',
            'duration',
            'task',
        ],
        'sort columns':[
            'type',
            'startdate',
            'source',
            'title',
            'starttime',
        ],
    }
    OLDEST_CONVERTIBLE_THEME_VERSION = [1,0,0]
    DEFAULT_THEME = {
        'version':[1,0,0],
        'base':{
            'widget':{},
            'labels':{},
            'entries':{},
            'buttons':{},
            'export button':{},
        },
        'fonts':{
            'labels':{'size':12,},
            'entries':{'size':12,},
            'buttons':{'size':12,},
            'export button':{'size':12,},
        },
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
        if oldsettings['version'] > CSVExport.DEFAULT_SETTINGS['version']:
            raise VersionException(VersionException.TOO_NEW,
                oldsettings['version'],CSVExport.DEFAULT_SETTINGS['version'])

        # If the old version is too old, we will not know how to convert
        if oldsettings['version'] \
            < CSVExport.OLDEST_CONVERTIBLE_SETTINGS_VERSION:
            raise VersionException(VersionException.TOO_OLD,
                oldsettings['version'],CSVExport.DEFAULT_SETTINGS['version'])

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
        if oldtheme['version'] > CSVExport.DEFAULT_THEME['version']:
            raise VersionException(VersionException.TOO_NEW,
                oldtheme['version'],CSVExport.DEFAULT_THEME['version'])

        # If the old version is too old, we will not know how to convert
        if oldtheme['version'] < CSVExport.OLDEST_CONVERTIBLE_THEME_VERSION:
            raise VersionException(VersionException.TOO_OLD,
                oldtheme['version'],CSVExport.DEFAULT_THEME['version'])

        # Finally, convert incrementally through all the versions
        # Below is some sample code to copy:
        #if oldtheme['version'] < [1,1]:
        #    oldtheme['somevariable'] = oldtheme['oldvariable']
        #    oldtheme['version'] = [1,1]

    def __init__ (self, parent, data, settings=None, theme=None,
        *args, **options):
        """CSVExport constructor
        settings and theme are pre-populated versions of each of the defaults
        defined within this class, for initializing a CSV export widget with
        non-default settings/theme.
        data is the timer data. It will be parsed and separated into the
        exported slices.
        """
        super().__init__(parent,*args,**options)
        # Associate this popup with the parent, and prevent it from showing as
        # a separate window
        self.transient(parent)
        # Name it
        self.title("YATTi CSV Export")
        # Prevent interaction with parent window
        self.grab_set()
        # Redirect window-closes to the cancel function
        self.protocol("WM_DELETE_WINDOW",self._cancel_export)

        ### Initialize internal variables
        self._all_timers = data['timerdata']
        # Store the parent window for later reference
        self._parent = parent
        # Result for the parent after closing this window
        self._result = 'norun'

        # Update the settings and theme parameters (or set to defaults)
        self._settings = helper.dictVersionUpdate(
            settings,
            self._settings_version_update,
            self.DEFAULT_SETTINGS
        )
        self._theme = helper.dictVersionUpdate(
            theme,
            self._theme_version_update,
            self.DEFAULT_THEME
        )
        # Filling from defaults the first time does not fill in the lists, so
        # we need to do so
        if len(self._settings['export columns']) == 0:
            self._settings['export columns'] = \
                self.DEFAULT_SETTINGS['export columns'][:]
        if len(self._settings['sort columns']) == 0:
            self._settings['sort columns'] = \
                self.DEFAULT_SETTINGS['sort columns'][:]

        ### Build the frame
        # Fonts
        self._font_entries = tkfont.Font()
        self._font_buttons = tkfont.Font()
        self._font_labels = tkfont.Font()
        self._font_exportbutton = tkfont.Font()
        # File selector
        fileframe = tk.Frame(self)
        fileframe.pack()
        self._filepath_entry = tk.Entry(
            fileframe,
            text='',
            font=self._font_entries,
            width=self._settings['filepath width'],
            state='readonly'
        )
        self._filepath_entry.pack(side='left')
        self._filepath_button = tk.Button(fileframe,text="Choose Directory",
            font=self._font_buttons,command=self._choose_directory)
        self._filepath_button.pack(side='left')
        # Export button
        exportframe = tk.Frame(self)
        exportframe.pack()
        self._cancel_button = tk.Button(
            exportframe,
            text="Cancel",
            font=self._font_buttons,
            command=self._cancel_export
        )
        self._cancel_button.pack(side='left')
        self._export_button = tk.Button(
            exportframe,
            text="Export",
            font=self._font_exportbutton,
            command=self._run_export
        )
        self._export_button.pack(side='left')

        # Update the theme from the dicts
        self.update_data()
        self.update_theme()

        self._filepath_entry.focus_set()
        self.after(10,self._center_on_parent)

    def _center_on_parent (self):
        """_center_on_parent callback function
        Centers this toplevel widget over the parent window. Makes sure
        the toplevel widget is sized before moving it.
        """
        if not self.winfo_viewable():
            self.after(10,self._center_on_parent)
            return
        selfwidth = self.winfo_width()
        selfheight = self.winfo_height()
        parentwidth = self._parent.winfo_width()
        parentheight = self._parent.winfo_height()
        xpos = (parentwidth/2)-(selfwidth/2)+self._parent.winfo_x()
        ypos = (parentheight/2)-(selfheight/2)+self._parent.winfo_y()
        self.geometry("+{}+{}".format(int(xpos),int(ypos)))

    def _choose_directory (self):
        """_choose_directory internal function
        Pops up a directory-chooser dialog.
        """
        new_directory = tkfiledialog.askdirectory(
            initialdir=self._settings['filepath'],
            mustexist=True
        )
        if new_directory != '':
            self._settings['filepath'] = new_directory
            self._update_filepath_entry()

    def _cancel_export (self):
        """_cancel_export internal function
        Cancels the export gracefully. For now, that just means killing
        the toplevel.
        """
        self._result = 'cancelled'
        self._close_window()

    def _run_export (self):
        """_run_export internal function
        Exports the calculated data to the indicated file and, if the user
        chose to, switches the exported flag on each of the newly-exported
        intervals.
        Internal dev note: It is assumed that update_data has already been
        run with the most recent user-selections. As such, any changes to
        user-selections should automatically run update_data.
        """
        timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime())
        filename = self._settings['filename'].format(
            timestamp=timestamp,fullsummary=self._fullsummary
        )
        filename = self._settings['filepath']+filename
        try:
            with open(filename,'w') as f:
                f.writelines([",".join(self._settings['export columns'])])
                f.write("\n")
                for row in self._export_rows:
                    for i,item in enumerate(row):
                        if i > 0:
                            f.write(",")
                        if "," in item:
                            f.write("\""+item+"\"")
                        else:
                            f.write(item)
                    f.write("\n")

            if self._settings['mark as exported']:
                for timer in self._export_timers:
                    for interval in timer['intervals']:
                        interval[2] = True

            self._result = 'success'
            tkmessagebox.showinfo("Export Successful",
                "Export to {} succeeded.\n{} rows exported.".format(
                    filename,len(self._export_rows)
                )
            )
        except:
            # TODO: implement debug logging
            #traceback.print_exc(file=self._logfile)
            tkmessagebox.showerror("Export Failed",
                "Export to {} failed.\nError traceback:\n{}".format(
                    filename,traceback.format_exc()
                )
            )
            self._result = 'failure'
        self._close_window()

    def _close_window (self):
        """_close_window internal function
        Gracefully closes the window, handing control back to the parent.
        """
        self._parent.focus_set()
        self.destroy()

    def update_data (self):
        """update_data function
        Updates the file-chooser entry based on chosen directory and options.
        Also updates the preview window based on options. In the background,
        it updates the calculations for same.
        """
        ### Update settings from entries/radiobuttons/checkboxes first
        self._fullsummary = 'fullsummary'

        ### Update calculations next
        # Gather all unexported timeslices
        self._export_timers = []
        for timer in self._all_timers:
            intervals = []
            for interval in timer['intervals']:
                # If not exported yet, add it to the slices to export
                if self._settings['export all slices'] or not interval[2]:
                    intervals.append(interval)
            # If any slices should be exported, add this timer and its slices
            if len(intervals) > 0:
                export_timer = {}
                export_timer['title'] = timer['title']
                export_timer['description'] = timer['description']
                export_timer['source system'] = timer['source system']
                export_timer['intervals'] = intervals
                self._export_timers.append(export_timer)
        # Calculate and flatten slices
        flat_rows = []
        summed_durations = {}
        summed_tasks = {}
        for timer in self._export_timers:
            for interval in timer['intervals']:
                # Flatten interval for full rows
                row = {}
                row['source'] = timer['source system']
                row['title'] = timer['title']
                row['description'] = timer['description']
                row['previousexport'] = str(interval[2])
                row['task'] = interval[3]
                row['startdate'] = time.strftime(
                    self._settings['time formats']['date'],
                    time.localtime(interval[0])
                )
                row['starttime'] = time.strftime(
                    self._settings['time formats']['time'],
                    time.localtime(interval[0])
                )
                row['endtime'] = time.strftime(
                    '%H:%M',
                    time.localtime(interval[1])
                )
                duration = (interval[1]-interval[0])/60/60
                row['rawduration'] = duration
                flat_rows.append(row)
                # Sum the durations and tasks for summary rows
                key = (
                    row['source'],
                    row['title'],
                    row['description'],
                    row['startdate']
                )
                if key not in summed_durations:
                    summed_durations[key] = 0
                    summed_tasks[key] = ""
                summed_durations[key] += duration
                if len(row['task']) > 0:
                    if len(summed_tasks[key]) > 0:
                        summed_tasks[key] += " "+row['task']
                    else:
                        summed_tasks[key] += row['task']
                    if summed_tasks[key][-1] not in (".",";"):
                        summed_tasks[key] += "."
        # Build the full and summary rows, according to settings
        self._export_rows = []
        if self._settings['export full rows']:
            durationformat = self._settings['time formats']['duration']['full']
            for row in flat_rows:
                rawhours = row['rawduration']
                inthours = int(rawhours)
                intminutes = int((rawhours-inthours)*60)
                roundingamount = self._settings['time formats'] \
                    ['duration']['roundingamount']
                roundedhours = round(rawhours/roundingamount)*roundingamount
                export_row = []
                for column in self._settings['export columns']:
                    if column == 'type':
                        export_row.append("Full")
                    elif column == 'duration':
                        duration = durationformat.format(
                            rawhours=rawhours,
                            inthours=inthours,
                            intminutes=intminutes,
                            roundedhours=roundedhours
                        )
                        export_row.append(duration)
                    elif column in row:
                        export_row.append(row[column])
                    else:
                        # TODO: Add debug logging here
                        export_row.append("")
                self._export_rows.append(export_row)
        if self._settings['export summary rows']:
            durationformat = self._settings['time formats'] \
                ['duration']['summary']
            for key in summed_durations:
                # key = (source,title,description,startdate)
                rawhours = summed_durations[key]
                task = summed_tasks[key]
                inthours = int(rawhours)
                intminutes = int((rawhours-inthours)*60)
                roundingamount = self._settings['time formats'] \
                    ['duration']['roundingamount']
                roundedhours = round(rawhours/roundingamount)*roundingamount
                export_row = []
                for column in self._settings['export columns']:
                    if column == 'type':
                        export_row.append("Summary")
                    elif column == 'source':
                        export_row.append(key[0])
                    elif column == 'title':
                        export_row.append(key[1])
                    elif column == 'description':
                        export_row.append(key[2])
                    elif column == 'startdate':
                        export_row.append(key[3])
                    elif column == 'duration':
                        duration = durationformat.format(
                            rawhours=rawhours,
                            inthours=inthours,
                            intminutes=intminutes,
                            roundedhours=roundedhours
                        )
                        export_row.append(duration)
                    elif column == 'task':
                        export_row.append(task)
                    else:
                        export_row.append("")
                self._export_rows.append(export_row)
        # Finally, sort the export rows according to settings
        sort_indexes = []
        for column in self._settings['sort columns']:
            if column in self._settings['export columns']:
                sort_indexes.append(
                    self._settings['export columns'].index(column)
                )
        self._export_rows.sort(
            key=lambda row,sort_indexes=sort_indexes: \
                [row[i] for i in sort_indexes]
        )

        ### Update displays
        self._update_filepath_entry()
        # No preview window to update yet

    def _update_filepath_entry (self):
        """_update_filepath_entry internal function
        Updates the text for the filepath entry box to reflect the
        newly-selected directory.
        """
        if len(self._settings['filepath']) > 0 \
            and self._settings['filepath'][-1] != '/':
            self._settings['filepath'] += '/'
        timestamp = time.strftime('%Y%m%d%H%M%S',time.localtime())
        filename = self._settings['filename'].format(
            timestamp=timestamp,fullsummary=self._fullsummary
        )
        state = self._filepath_entry.cget('state')
        self._filepath_entry.config(state='normal')
        if self._filepath_entry.get() == "":
            self._filepath_entry.insert(0,"blah")
        self._filepath_entry.delete(0,tk.END)
        self._filepath_entry.insert(0,self._settings['filepath']+filename)
        self._filepath_entry.config(state=state)

    def update_theme (self):
        """update_theme function
        Updates the fonts/colors/styles from the theme attribute. Used when
        the user changes the theme.
        """
        widgets = (
            (self,'widget'),
            (self._filepath_entry,'entries'),
            (self._filepath_button,'buttons'),
            (self._cancel_button,'buttons'),
            (self._export_button,'buttons'),
            (self._export_button,'export button'),
        )
        fontwidgets = (
            (self._font_buttons,'buttons'),
            (self._font_entries,'entries'),
            (self._font_exportbutton,'export button'),
            (self._font_labels,'labels'),
        )

        # Update the theme for each of the sub-widgets and fonts
        for widget,name in widgets:
            helper.configThemeFromDict(widget,self._theme,'base',name)
        for widget,name in fontwidgets:
            helper.configThemeFromDict(widget,self._theme,'fonts',name)


if __name__ == "__main__":
    import traceback
    try:
        def on_close ():
            for timer in timers:
                timer.running = False
            root.destroy()
        def togglecallback (atimer):
            if atimer.running:
                for timer in timers:
                    if timer != atimer:
                        timer.running = False
        def labelcallback (atimer):
            for interval in atimer._data['intervals']:
                print(
                    time.strftime(
                        '%Y/%m/%d %H:%M:%S',time.localtime(interval[0])
                    ),
                    '-',
                    time.strftime(
                        '%Y/%m/%d %H:%M:%S',time.localtime(interval[1])
                    )
                )
            print()
        root = tk.Tk()
        timers = []
        timer_datas = [
            {
                'title':"COE-4840",
                'description':"A really long, verbose, complicated pile" \
                    + " of junk",
                'intervals':[[0,3500,False,"Blah"]],
            },
            {'title':"Other timer",'description':"Some short text"},
            {'title':"Yet another timer",'description':"Words"}
        ]
        frame = tk.Frame(root,width=400,height=200)
        frame.pack(fill='both',expand=True)
        for data in timer_datas:
            timer = TimerButton(frame, timerdata=data)
            timer.pack()
            timer.register_toggle_callback(togglecallback)
            timer.register_labelclick_callback(labelcallback)
            timers.append(timer)
        root.protocol('WM_DELETE_WINDOW',on_close)
        root.mainloop()
    except Exception as e:
        print()
        traceback.print_exc()
    finally:
        input("Press enter to quit")

