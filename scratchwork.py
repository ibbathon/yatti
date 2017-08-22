from section import Section
from tkinter import Tk, Frame, Label, Entry, Button, Text, messagebox, END
import time

def on_closing ():
	root.iconify()

def on_change (action,initial_value,new_value,action_type):
	# Check if the new value is a valid number
	valid_num = False
	try:
		float(new_value)
		valid_num = True
	except:
		pass
	# If it's a valid number or blank, then it's a valid entry
	if valid_num or new_value == "":
		return True
	# Otherwise, it's an invalid entry that shouldn't be saved
	# However, we should check for the parts of a number, in case it's partially typed in
	for char in new_value:
		if char not in '-.0123456789':
			return False
	# All of the characters are valid, even if it's not a valid number, so allow it to be typed
	return True

def pad_int (val, min_digits, char='0'):
	string = str(val)
	if min_digits > len(string):
		string = char*(min_digits-len(string))+string
	return string

def tick ():
	timer_end_time = time.time()
	el_time = int(timer_end_time-timer_start_time)
	el_time_seconds = el_time % 60
	el_time_minutes = int(el_time / 60) % 60
	el_time_hours = int(el_time / 3600)
	el_time_as_string = pad_int(el_time_seconds,2)
	if el_time_minutes > 0 or el_time_hours > 0:
		el_time_as_string = pad_int(el_time_minutes,2)+':'+el_time_as_string
		if el_time_hours > 0:
			el_time_as_string = pad_int(el_time_hours,2)+':'+el_time_as_string
	other_entry.delete(0,END)
	other_entry.insert(0,el_time_as_string)
	other_entry.after(500,tick)

if __name__ == '__main__':
	root = Tk()
	on_change_reg = root.register(on_change)

	# first section
	section1 = Section(root, text='First Section')
	section1.pack(fill='x', expand=True, anchor='nw')
	Label(section1.sub_frame, text='Inside first section', bg='white').pack(expand=False,
			anchor='w')

	# second section
	section2 = Section(root, text='Second Section')
	section2.pack(fill='x', expand=True, anchor='nw')
	line_frame = Frame(section2.sub_frame)
	line_frame.pack(expand=True, anchor='w')
	Entry(line_frame, validate='all',
		validatecommand=(on_change_reg,'%d','%s','%P','%V')).pack(side='left')
	Button(line_frame, text='Actually Quit', command=root.destroy).pack(side='left')
	inner_section1 = Section(section2.sub_frame,text='Inner Section 1')
	inner_section1.pack(fill='x', expand=True, anchor='nw')
	other_entry = Entry(inner_section1.sub_frame)
	other_entry.pack(anchor='w')
	inner_section2 = Section(section2.sub_frame,text='Inner Section 2')
	inner_section2.pack(fill='x', expand=True, anchor='nw')
	Label(inner_section2.sub_frame,text='I\'m inside...').pack(anchor='w')

	# third section
	section3 = Section(root, text='Third Section')
	section3.pack(fill='x', expand=True, anchor='nw')
	Text(section3.sub_frame).pack(anchor='w')

	root.protocol("WM_DELETE_WINDOW",on_closing)

	# Start a timer before starting the Tk loop
	timer_start_time = time.time()
	other_entry.after(500,tick)

	root.mainloop()
