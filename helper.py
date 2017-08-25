"""helper module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-25
Description = Provides some helper functions and constants for use in my other programs.
"""
PLAY_CHAR=u'\u23F5'
PAUSE_CHAR=u'\u23F8'
LEFT_CHAR=u'\u23F4'
RIGHT_CHAR=u'\u23F5'
NUM_WEEKDAYS=7
WEEKDAYS=(
	("S","U","Su","Sun","Sunday"),
	("M","M","Mo","Mon","Monday"),
	("T","T","Tu","Tue","Tuesday"),
	("W","W","We","Wed","Wednesday"),
	("T","H","Th","Thu","Thursday"),
	("F","F","Fr","Fri","Friday"),
	("S","S","Sa","Sat","Saturday")
)
WEEKDAYS_1_LETTER=tuple([WEEKDAYS[i][0] for i in range(len(WEEKDAYS))])
WEEKDAYS_1_LETTER_UNIQUE=tuple([WEEKDAYS[i][1] for i in range(len(WEEKDAYS))])
WEEKDAYS_2_LETTER=tuple([WEEKDAYS[i][2] for i in range(len(WEEKDAYS))])
WEEKDAYS_3_LETTER=tuple([WEEKDAYS[i][3] for i in range(len(WEEKDAYS))])
WEEKDAYS_FULL=tuple([WEEKDAYS[i][4] for i in range(len(WEEKDAYS))])
NUM_MONTHS=12
MAX_WEEKS_IN_MONTH=6
MONTHS=(
	("Jan","January"),
	("Feb","February"),
	("Mar","March"),
	("Apr","April"),
	("May","May"),
	("Jun","June"),
	("Jul","July"),
	("Aug","August"),
	("Sep","September"),
	("Oct","October"),
	("Nov","November"),
	("Dec","December")
)
MONTHS_3_LETTER=tuple([MONTHS[i][0] for i in range(len(MONTHS))])
MONTHS_FULL=tuple([MONTHS[i][1] for i in range(len(MONTHS))])

def dictFromDefaults (custom, defaults):
	"""setDictFromDefaults helper function
	Returns a dict with settings from custom and default settings from defaults.
	If custom is None or not a dict, then it returns a new dict. Otherwise, it modifies custom
	and returns a reference.
	"""
	if custom == None or type(custom) != type({}):
		custom = {}

	for k in defaults.keys():
		# If the key is not in custom or defaults[k] is a dict and custom[k] is not
		if k not in custom or (type(defaults[k]) == type({}) and type(custom[k]) != type({})):
			# If it should be a dict
			if type(defaults[k]) == type({}):
				# Create a blank new dict
				custom[k] = {}
			# Otherwise, just copy the value from defaults
			elif type(defaults[k]) == type([]):
				custom[k] = []
			else:
				custom[k] = defaults[k]
		# If it's a dict, we need to recurse into it
		if type(defaults[k]) == type({}):
			dictFromDefaults(custom[k],defaults[k])
		# Otherwise, we're done with this key

	# Now we're done with copying everything on this level, so back up to the previous level
	return custom

def configThemeFromDict (widget, theme, themetype, widgettype):
	"""configThemeFromDict helper function
	If themetype exists in the theme dict and widgettype exists in theme[themetype],
	then configure the widget using the theme.
	If themetype is fonts, then use ** to expand the theme, as it does not work otherwise.
	"""
	if themetype in theme and widgettype in theme[themetype]:
		if themetype == 'fonts':
			widget.configure(**theme[themetype][widgettype])
		else:
			widget.configure(theme[themetype][widgettype])
