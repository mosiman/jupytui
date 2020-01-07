import urwid

# Monkeypatch: issue 386

import patch_issue_386
urwid.ListBox = patch_issue_386.ListBox

import nbformat
from rework_widgets import Cell, NotebookWalker, PopUpDialog, SelectableEdit, StatefulFrame

import logging
logging.basicConfig(filename='rework.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

palette = [
        ('fnamebox', 'black', 'white'),
        ('bg', 'black', 'dark blue'),
        ('cellFocus', 'light green', ''),
        ('foot', 'yellow', 'dark gray'),
        ('regularText', '', ''),         # so attrmap(linebox) doesn't assign to text
        ('regularLineBox', '', ''),         # so attrmap(linebox) doesn't assign to text
        ]

# read a notebook
fname = 'census.ipynb'
nbk = nbformat.read(fname, nbformat.NO_CONVERT)

####### SIGNALS #########

def undoOverlayMessage():
    loop.widget = loop.widget.bottom_w

def debug_input(key):
    logging.debug(f"unhandled key: {key}")
    if key == 'f4':
        logging.debug('f4 pressed')
        pop_up = PopUpDialog("foobar!")
        overlay = urwid.Overlay(pop_up, loop.widget, align='center', width=('relative', 80), valign='middle', height=('relative', 80))
        loop.widget = overlay
        urwid.connect_signal(pop_up, 'close',
                lambda button: undoOverlayMessage())
    if key == 'f1':
        logging.debug(f'cell[2]: {loop.widget.body.body.cells[2]}')
    if key == 'f2':
        logging.debug(f'f2 pressed')
        logging.debug(f'Setting cell[2] editbox to be not selectable')
        SelectableEdit._selectable = False
    if key == 'f3':
        logging.debug(f'f3 pressed')
        logging.debug(f'Setting editboxes to be selectable again')
        SelectableEdit._selectable = True


nbkWalker = NotebookWalker(nbk)
listcell = urwid.ListBox(nbkWalker)

cmdbox = urwid.Edit(edit_text="(NAV)")
fnamebox = urwid.AttrMap(urwid.Text(fname), 'fnamebox')
footer = urwid.Pile([fnamebox, cmdbox])

#frame = urwid.Frame(listcell, footer=footer)

frame = StatefulFrame(listcell, footer=footer)

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True)

loop.run()
