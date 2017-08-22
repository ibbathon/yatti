"""helper module
Author = Richard D. Fears
Created = 2017-08-22
LastModified = 2017-08-22
Description = Provides some helper functions and constants for use in my other programs.
"""
PLAY_CHAR=u'\u23F5'
PAUSE_CHAR=u'\u23F8'

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
