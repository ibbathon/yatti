from accordion import Accordion, Chord
from tkinter import Tk, Label, Entry, Button, Text, messagebox

def on_closing ():
	root.iconify()

def on_change (action,initial_value,final_value,action_type):
	valid_num = False
	try:
		float(final_value)
		valid_num = True
	except:
		pass
	if valid_num or final_value == "" or final_value in ('-','.'):
		return True
	return False

if __name__ == '__main__':
	root = Tk()
	on_change_reg = root.register(on_change)

	# create the Accordion
	acc = Accordion(root)

	# first chord
	first_chord = Chord(acc, title='First Chord', bg='white')
	Label(first_chord, text='Inside first chord', bg='white').pack()

	# second chord
	second_chord = Chord(acc, title='Second Chord', bg='white')
	entry = Entry(second_chord, validate='all',
		validatecommand=(on_change_reg,'%d','%s','%P','%V'))
	entry.grid(row=0,column=0)
	button = Button(second_chord, text='Actually Quit', command=root.destroy)
	button.grid(row=0,column=1)
	inner_accordion = Accordion(second_chord)
	inner_chord1 = Chord(inner_accordion,title='Inner Chord 1',bg='red')
	Entry(inner_chord1).pack()
	inner_chord2 = Chord(inner_accordion,title='Inner Chord 2',bg='red')
	Label(inner_chord2,text='I\'m inside...').pack()
	inner_accordion.append_chords([inner_chord1,inner_chord2])
	inner_accordion.grid(row=1,column=0,columnspan=2,sticky='w')

	# third chord
	third_chord = Chord(acc, title='Third Chord', bg='white')
	Text(third_chord).pack()

	# append list of chords to Accordion instance
	acc.append_chords([first_chord, second_chord, third_chord])
	acc.pack()

	root.protocol("WM_DELETE_WINDOW",on_closing)
	root.mainloop()
