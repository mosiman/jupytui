
import logging

logging.basicConfig(filename='rework.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

import urwid

# Let's try to get the listbox display going.

import nbformat

from rework_widgets import Cell, NotebookWalker, helpOverlay, overlayMessage, OverlayButton, TestPopupLauncher, PopUpDialog

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

####### SIGNALS #########


def undoOverlayMessage():
    loop.widget = loop.widget.bottom_w

def debug_input(key):
    logging.debug(f"unhandled key: {key}")
    if key == 'f1':
        loop.widget = overlayMessage(helpOverlay, loop.widget)
    if key == 'f2':
        loop.widget.open_pop_up()
    if key == 'f3':
        logging.debug('f3 pressed')
        pop_up = PopUpDialog("foobar!")
        overlay = urwid.Overlay(pop_up, loop.widget, align='center', width=('relative', 80), valign='middle', height=('relative', 80))
        loop.widget = overlay
        urwid.connect_signal(pop_up, 'close',
                lambda button: undoOverlayMessage())



nbkWalker = NotebookWalker(nbk)

listcell = urwid.ListBox(nbkWalker)

footer = urwid.Text(" F1: Help || F2 (shift): Save (as) || F3: Open")

frame = urwid.Frame(listcell, footer=footer)

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True)

loop.run()
