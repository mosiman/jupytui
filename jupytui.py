import urwid
import sys
import logging
import zmq_loop.urwid_zmq_event_loop

import pprint

pprint.PrettyPrinter(indent=4)

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

    if key == 'f1':
        logging.debug(pprint.pformat(loop.widget.listbox.body[3].lineBorder.title_widget))

def recvIopubMsg(msg):
    logging.debug(f"recvIopubMsg: {msg}")
    if "parent_header" in msg and "msg_id" in msg["parent_header"]:
        parent = msg["parent_header"]["msg_id"]
        if parent in requestManager:
            requestManager[parent].handleChildMessage(msg)

def recvShellMsg(msg):
    logging.debug(f"recvShellMsg: {msg}")
    if "parent_header" in msg and "msg_id" in msg["parent_header"]:
        parent = msg["parent_header"]["msg_id"]
        if parent in requestManager:
            requestManager[parent].handleChildMessage(msg)

def quit():
    # TODO: gracefully stop jupyter processes, or wrap in some session manager.
    raise urwid.ExitMainLoop()

def executeCell(cell: JupytuiWidgets.Cell):
    # nbkNode = cell.asNotebookNode()
    # msgid = kerClient.execute(nbkNode.source)
    # logging.debug(f"executed! id: {msgid}")
    r = ExecuteRequest(kerClient, cell)
    requestManager[r.msg_id] = r


def read_messages():
    msg = kerClient.get_iopub_msg()
    logging.debug(f"iopub: {msg}")

class ExecuteRequest:
    def __init__(self, ctx, cell):
        self.cell = cell
        self.msg_id = ctx.execute(self.cell.asNotebookNode().source)
        self.cell.clearOutputs()

    def handleChildMessage(self, msg):
        logging.debug(f"handling message!")

        # the execution number is in the execute_input reply
        execnum = None
        if msg["msg_type"] == 'execute_reply':
            execnum = msg['content']['execution_count']
            self.cell.lineBorder.set_title(f"In [{execnum}]")
        try:
            newOut = nbformat.v4.output_from_msg(msg)
            self.cell.appendOutput(newOut)
        except ValueError:
            # if msg_type is not acceptable (e.g. status, execute_input, etc)
            pass


# TODO build a proper way to manage requests!!!
# dict could have arbitrary amount of keys, not good...
# lots of deletion / additions, hash space is bad?
# look into weakref dicts? or custom made object, maybe..
requestManager = {}

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

jc_eventloop = zmq_loop.urwid_zmq_event_loop.ZmqEventLoop(ctx=kerClient)
jc_eventloop.register_channels()

loop = urwid.MainLoop(frame, palette, unhandled_input=debug_input, pop_ups=True, event_loop=jc_eventloop)

####### SIGNALS #########

# Handle commands from the commandbox
urwid.register_signal(urwid.Edit, ['cmdOpen', 'cmdWrite', 'cmdListKernels', 'cmdExecuteCurrentCell', 'cmdQuit'])
urwid.connect_signal(loop.widget.cmdbox, 'cmdQuit', quit)
urwid.connect_signal(loop.widget.cmdbox, 'cmdOpen', resetNotebook)
urwid.connect_signal(loop.widget.cmdbox, 'cmdWrite', saveNotebook)
urwid.connect_signal(loop.widget.cmdbox, 'cmdListKernels', listKernels)
urwid.connect_signal(loop.widget.cmdbox, 'cmdExecuteCurrentCell', executeCell)

# Handle messages from the Kernel
urwid.connect_signal(loop.event_loop, 'iopubMsg', recvIopubMsg)
urwid.connect_signal(loop.event_loop, 'shellMsg', recvShellMsg)

loop.run()
