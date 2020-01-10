import urwid

# Monkeypatch: issue 386

import patch_issue_386
urwid.ListBox = patch_issue_386.ListBox

import nbformat
from JupytuiWidgets import Cell, NotebookWalker, PopUpDialog, SelectableEdit
from State import StatefulFrame

import logging
logging.basicConfig(filename='loggy.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

palette = [
        ('fnamebox', 'black', 'white'),
        ('bg', 'black', 'dark blue'),
        ('cellFocus', 'light green', ''),
        ('foot', 'yellow', 'dark gray'),
        ('regularText', '', ''),         # so attrmap(linebox) doesn't assign to text
        ('regularLineBox', '', ''),         # so attrmap(linebox) doesn't assign to text
        ]

def openNotebook(fname):
    nbk = nbformat.read(fname, nbformat.NO_CONVERT)
    nbkWalker = NotebookWalker(nbk)
    listcell = urwid.ListBox(nbkWalker)

    cmdbox = urwid.Edit(edit_text="(NAV)")
    fnamebox = urwid.AttrMap(urwid.Text(fname), 'fnamebox')
    footer = urwid.Pile([fnamebox, cmdbox])

    frame = StatefulFrame(listcell, footer=footer)

    return frame

def resetNotebook(fname):
    newFrame = openNotebook(fname)
    loop.widget = newFrame
    # new cmdbox: gotta register again.
    urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)

def undoOverlayMessage():
    loop.widget = loop.widget.bottom_w

def debug_input(key):
    logging.debug(f"unhandled key: {key}")

# read a notebook
fname = 'census.ipynb'
frame = openNotebook(fname)

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True)

####### SIGNALS #########

# Handle commands from the commandbox
urwid.register_signal(urwid.Edit, ['cmdOpen'])
urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)

loop.run()
