
import logging

logging.basicConfig(filename='rework.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

import urwid

# Let's try to get the listbox display going.

import nbformat

from rework_widgets import Cell, NotebookWalker, CloneWalker, NotebookWalkerV1

palette = [
        ('banner', 'black', 'light gray'),
        ('streak', 'black', 'dark red'),
        ('bg', 'black', 'dark blue'),
        ('cellFocus', 'light green', ''),
        ('foot', 'yellow', 'dark gray'),
        ('regularText', '', ''),         # so attrmap(linebox) doesn't assign to text
        ('regularLineBox', '', ''),         # so attrmap(linebox) doesn't assign to text
        ]

# read a notebook

nbk = nbformat.read('census.ipynb', nbformat.NO_CONVERT)

# View (Listbox)
#  |
#  |-- Notebook Cell 1 (Pile)
#  |    |
#  |    |-- Notebook Source (Edit) [[Decorate: Linebox]]
#  |    |
#  |    |-- Notebook Output 1 (Text)
#  |    |
#  |    |-- Notebook Output ... (Text)
#  |    |
#  |    |-- Notebook Output n (Text)
#  |
#  |-- Notebook Cell 2 (Pile)
#       |
#       |-- Notebook Source (Edit) [[Decorate: Linebox]]
#       |
#       |-- Notebook Output 1 (Text)
#       |
#       |-- Notebook Output ... (Text)
#       |
#       |-- Notebook Output n (Text)


def debug_input(key):
    logging.debug(f"unhandled key: {key}")

simpleLW = urwid.SimpleFocusListWalker([])

cloneLW = CloneWalker([])

for cell in nbk.cells:
    simpleLW.append(Cell(cell))
    #cloneLW.append(Cell(cell))

nbkWalker = NotebookWalker(nbk)
#nbkWalker = NotebookWalkerV1(nbk)

# listcell = urwid.ListBox(simpleLW)
listcell = urwid.ListBox(nbkWalker)

#listcell = urwid.ListBox(cloneLW)

loop = urwid.MainLoop(listcell, palette, unhandled_input=debug_input)

loop.run()
