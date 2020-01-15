import urwid
import sys
import logging

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

def currentNotebook(nbkWalker):
    newNbk = nbformat.v4.new_notebook()
    newNbk.metadata = nbkWalker.nbk.metadata
    # nbk = nbkWalker.nbk

    # cells = nbk.cells

    # for cell in cells:
    #     src = cell.source
    #     if cell.cell_type == 'code':
    #         nbkCell = nbformat.v4.new_code_cell(source = src)
    #         # NOTE cell.outputs should be up to date
    #         # i.e., update it when we get the appropriate IOPub msg via nbformat.v4.output_from_msg
    #         nbkCell.execution_count = cell.execution_count
    #         nbkCell.outputs = cell.outputs
    #     elif cell.cell_type == 'markdown':
    #         nbkCell = nbformat.v4.new_markdown_cell(source = src)
    #     elif cell.cell_type == 'raw':
    #         nbkCell = nbformat.v4.new_raw_cell(source = src)
    #     else:
    #         raise ValueError
    #     newNbk.cells.append(nbkCell)
    for cell in nbkWalker.cells:
        newNbk.cells.append(cell.asNotebookNode())
    return newNbk


def saveNotebook():
    newNbk = currentNotebook(loop.widget.listbox.body)
    nbformat.write(newNbk, 'censusNEW.ipynb')



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
    urwid.disconnect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)
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

# empty notebook
# nbk = nbformat.v4.new_notebook()
# nbkWalker = NotebookWalker(nbk)
# listcell = urwid.ListBox(nbkWalker)
# 
# cmdbox = urwid.Edit(edit_text="(NAV)")
# fnamebox = urwid.AttrMap(urwid.Text("NEW"), 'fnamebox')
# footer = urwid.Pile([fnamebox, cmdbox])
# 
# frame = StatefulFrame(listcell, footer=footer)

if frame.listbox.body.nbk.nbformat != 4:
    upgradeOld = input("This is an old notebook version. Upgrade to 4? [y/n]: ")
    if upgradeOld.lower() != 'y':
        sys.exit()


loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True)

####### SIGNALS #########

# Handle commands from the commandbox
urwid.register_signal(urwid.Edit, ['cmdOpen', 'cmdWrite'])
urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)
urwid.connect_signal(loop.widget.cmdbox, 'cmdWrite', saveNotebook)

loop.run()
