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

def replaceNotebook(fname):
    logging.debug('replaceNotebook called')
    frame = openNotebook(fname)
    loop.widget = frame
    SelectableEdit._selectable = True

def undoOverlayMessage():
    loop.widget = loop.widget.bottom_w

def debug_input(key):
    logging.debug(f"unhandled key: {key}")

    if key == 'f1':
        logging.debug(f'text in cell[3] {loop.widget.listbox.body.cells[3].editbox.original_widget.get_edit_text()}')
    if key == 'f2':
        logging.debug(f'cell[3] {loop.widget.listbox.body.cells[3].editbox.original_widget}')
    if key == 'f3':
        logging.debug(f"adding to cell[3]")
        loop.widget.listbox.body.cells[3].editbox.original_widget.edit_text += " foobar"
    if key == 'f4':
        logging.debug(f'focus path {loop.widget.get_focus_widgets()}')
    if key == 'f5':
        logging.debug(f'{loop.widget.listbox.body[0]}')
    if key == 'f6':
        logging.debug(f'{loop.widget.listbox.body[0]._w.contents}')
    if key == 'f7':
        # what does ._selectable say?
        logging.debug(f'editbox selectable: {loop.widget.listbox.body[0].editbox.original_widget.selectable()}')

# read a notebook
fname = 'census.ipynb'
frame = openNotebook(fname)

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True)

####### SIGNALS #########

# Handle commands from the commandbox
urwid.register_signal(urwid.Edit, ['cmdOpen', 'cmdWrite'])
urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', replaceNotebook)

loop.run()
