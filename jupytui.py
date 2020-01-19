import urwid
import sys
import logging
import zmq_loop.urwid_zmq_event_loop

# Monkeypatch: issue 386

import patch_issue_386
urwid.ListBox = patch_issue_386.ListBox

import nbformat
# from JupytuiWidgets import Cell, NotebookWalker, PopUpDialog, SelectableEdit, \
#                           PopUpListSelectText
import JupytuiWidgets 
from State import StatefulFrame

import jupyter_client as jc
kerSpecMan = jc.kernelspec.KernelSpecManager()


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

    for cell in nbkWalker.cells:
        newNbk.cells.append(cell.asNotebookNode())
    return newNbk


def saveNotebook():
    newNbk = currentNotebook(loop.widget.listbox.body)
    nbformat.write(newNbk, 'censusNEW.ipynb')


def listKernels():
    kspecs = kerSpecMan.find_kernel_specs()
    kernelNames = kspecs.keys()

    pop_up = JupytuiWidgets.PopUpListSelectText("Select kernel: ",[urwid.Text(k) for k in kernelNames])

    overlay = urwid.Overlay(pop_up, loop.widget, align='center', width=('relative', 80), valign='middle', height=('relative', 80))

    loop.widget = overlay

    urwid.connect_signal(pop_up, 'close',
        lambda button: selectKernel(button))

def selectKernel(widg):
    """
    changes the kernel. `widg` is a text widget with the name of the kernel
    """
    undoOverlayMessage()

    kernelName = widg.text
    loop.widget.kernelStatus.set_text(f"{kernelName} (connecting..)")
    # do an async thing here with jupyter_client

def openNotebook(fname):
    nbk = nbformat.read(fname, nbformat.NO_CONVERT)
    nbkWalker = JupytuiWidgets.NotebookWalker(nbk)
    listcell = urwid.ListBox(nbkWalker)

    cmdbox = urwid.Edit(edit_text="(NAV)")
    fnamebox = urwid.AttrMap(urwid.Text(fname), 'fnamebox')
    footer = urwid.Pile([fnamebox, cmdbox])

    try:
        kernelName = nbk.metadata.kernelspec.name
        kernelStatus = urwid.Text(kernelName)
    except AttributeError:
        kernelName = None

    header = urwid.Columns([urwid.Text("Jupytui"),kernelStatus])
    frame = StatefulFrame(listcell, footer=footer, header=header)

    return frame

def resetNotebook(fname):
    newFrame = openNotebook(fname)
    urwid.disconnect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)
    loop.widget = newFrame
    # new cmdbox: gotta register again.
    # TODO: replace just the body to avoid reregistering widgets.
    urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)

def undoOverlayMessage():
    loop.widget = loop.widget.bottom_w

def debug_input(key):
    logging.debug(f"unhandled key: {key}")

def recvIopubMsg(msg):
    logging.debug(f"recvIopubMsg: {msg}")

def executeCell(cell: JupytuiWidgets.Cell):
    nbkNode = cell.asNotebookNode()
    kerClient.execute(nbkNode.source)

def read_messages():
    msg = kerClient.get_iopub_msg()
    logging.debug(f"iopub: {msg}")


# read a notebook
fname = 'census.ipynb'
frame = openNotebook(fname)

if frame.listbox.body.nbk.nbformat != 4:
    upgradeOld = input("This is an old notebook version. Upgrade to 4? [y/n]: ")
    if upgradeOld.lower() != 'y':
        sys.exit()

# testing purposes:
kerMan = jc.KernelManager(kernel_name='python3')
kerMan.start_kernel()
kerClient = kerMan.client()
kerClient.start_channels()

jc_eventloop = zmq_loop.urwid_zmq_event_loop.ZmqEventLoop()
#jc_eventloop = JupytuiWidgets.JCEventLoop(kerClient)
jc_eventloop.watch_file(kerClient.iopub_channel.socket, read_messages)

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True, event_loop=jc_eventloop)

####### SIGNALS #########

# Handle commands from the commandbox
urwid.register_signal(urwid.Edit, ['cmdOpen', 'cmdWrite', 'cmdListKernels', 'cmdExecuteCurrentCell'])
urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)
urwid.connect_signal(loop.widget.cmdbox, 'cmdWrite', saveNotebook)
urwid.connect_signal(loop.widget.cmdbox, 'cmdListKernels', listKernels)
urwid.connect_signal(loop.widget.cmdbox, 'cmdExecuteCurrentCell', executeCell)

# urwid.connect_signal(loop.event_loop, 'iopubMsg', recvIopubMsg)

loop.run()
