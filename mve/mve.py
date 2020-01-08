import urwid
import logging

logging.basicConfig(filename='loggy.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

e1 = urwid.Edit(edit_text="These edit boxes are all editable")
e2 = urwid.Edit(edit_text="Press `esc`, which will replace the first edit box with a new one. It will no longer be editable")
e3 = urwid.Edit(edit_text="foo foo bar bar")

simpleLW = urwid.SimpleListWalker([e1, e2, e3])
listbox = urwid.ListBox(simpleLW)

def debug_input(key):
    logging.debug(f'uncaught input: {key}')
    if key == 'esc':
        simpleLW[0] = urwid.Edit(edit_text = "Wassup")

loop = urwid.MainLoop(listbox, [], unhandled_input=debug_input)

loop.run()
