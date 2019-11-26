import urwid 
import logging
# from pixcat import Image


import json

from NbkUrwid import NbkCellLineBox, NbkCellWalker, NbkListBox, \
                     NbkEditBox, \
                     NbkCellRaw, NbkCellMkdn, NbkCellCode

logging.basicConfig(filename='jupytui.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def show_or_exit(key):
    # print(f"unhandled key: {key}")
    # img = Image("/home/mosiman/test.png")
    # img.show(x=50, y=50)
    # modalLW.set_focus(modalLW.focus + 1)
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

palette = [
        ('banner', 'black', 'light gray'),
        ('streak', 'black', 'dark red'),
        ('bg', 'black', 'dark blue'),
        ('cellFocus', 'light green', ''),
        ('foot', 'yellow', 'dark gray')
        ]



def add_editbox(key):
    if key in ('q', 'Q'):
        # raise urwid.ExitMainLoop()
        nbkLW.append(urwid.LineBox(urwid.Text("sup2")))
    return True

def handleCodeOutput(outputs):
    outstr = ""
    for output in outputs:
        if output["output_type"] == 'stream':
            outstr += ' > ' + ' > '.join(output["text"])
        elif output["output_type"] == 'display_data':
            outstr += ' > << Some display data >>'
        elif output["output_type"] == 'execute_result':
            data = output["data"]
            for datatype in data.keys():
                if datatype == "text/plain":
                    outstr += ' > ' + ' > '.join(data['text/plain'])
                else:
                    outstr += f' > << Some {datatype} >> '
                outstr += '\n'
        outstr += '\n'
    return outstr

def chooseNbkCell(cell):
    if 'execution_count' in cell:
        runNum = cell['execution_count']
        logging.debug(f"execution count found: {cell['execution_count']}")
    else:
        runNum = ''

    if cell["cell_type"] == 'markdown':
        return NbkCellMkdn(''.join(cell["source"]), runNum=runNum)
    elif cell["cell_type"] == 'code':
        # process the output 
        out = handleCodeOutput(cell["outputs"])
        return NbkCellCode(''.join(cell["source"]), out, runNum=runNum)
    elif cell["cell_type"] == 'raw':
        return NbkCellRaw(''.join(cell["source"]), runNum=runNum)


class StatusBar(urwid.Edit):
    def __init__(self, caption=u"", edit_text=u"", multiline=False,
            align='left', wrap='space', allow_tab=False,
            edit_pos=None, layout=None, mask=None, selectable=False):
        super().__init__(caption=caption, edit_text=edit_text, multiline=multiline,
            align=align, wrap=wrap, allow_tab=allow_tab,
            edit_pos=edit_pos, layout=layout, mask=mask)

        self._selectable = selectable
        
    def selectable(self):
        return self._selectable
    def set_selectable(self,b):
        self._selectable = b

    def keypress(self, size, key):

        if key == 'enter':
            logging.debug(f"Command to be sent: {self.edit_text}")
            urwid.emit_signal(self, "modeChange", "NAV")
        elif key == 'backspace':
            if self.edit_pos == 1:
                urwid.emit_signal(self, "modeChange", "NAV")
            else:
                super().keypress(size,key)
        else:
            super().keypress(size, key)


class ModalManager:
    def __init__(self, mode='NAV'):
        self.mode = mode 

    def switch_mode(self, mode):
        self.mode = mode

class ModalFrame(urwid.Frame):
    def __init__(self, body, modeman, header=None, footer=None, focus_part='body'):
        super().__init__(body, header=header, footer=footer, focus_part=focus_part)
        self.modeman = modeman 

    def changeMode(self, mode):
        prevMode = self.modeman.mode 

        logging.debug(f"chageMode signal caught")
        logging.debug(f"prevmode: {prevMode}")
        logging.debug(f"mode: {mode}")

        if prevMode == 'NAV' and mode == 'COMMAND':
            logging.debug("prevmode NAV, mode COMMAND")
            # set focus to footer 
            self.footer.base_widget.set_selectable(True)
            self.footer.base_widget.set_edit_text(':')
            self.modeman.mode = mode
            self.focus_position = 'footer'
            pass
        elif prevMode == 'NAV' and mode == 'CELL':
            # focus should already be on body 
            self.modeman.mode = mode
            self.footer.base_widget.set_edit_text('Vi (CELL)')
            pass 
        elif prevMode == 'CELL' and mode == 'NAV':
            logging.debug("prevmode CELL, mode NAV")
            # focus should already be on body
            self.modeman.mode = mode
            self.footer.base_widget.set_edit_text('Vi (NAV)')
            pass
        elif prevMode == 'COMMAND' and mode == 'NAV':
            logging.debug("prevmode COMMAND, mode NAV")
            # set focus to body 
            self.footer.base_widget.set_selectable(False)
            self.footer.base_widget.set_edit_text('Vi (NAV)')
            self.modeman.mode = mode
            self.focus_position = 'body'
        self.modeman.mode == mode

    def keypress(self, size, key):
        """
        Going to manage how keypresses get filtered out to appropriate components.
        Let the children manage the switches.
        """
        logging.debug(f"keypress, modal frame with key {key}")
        
        #should use self.focus_position = 'body' instead of set_focus

        # if mode = 'NAV', should go to listbox 
        # if self.modeman == 'NAV':
        #     self.set_focus('body')
        # # if mode = 'CELL', should go to listbox 
        # if self.modeman == 'CELL':
        #     self.set_focus('body')
        # # if mode = 'COMMAND', should go to footer
        # if self.modeman == 'COMMAND':
        #     self.set_focus('footer')
        return super().keypress(size, key)


def modalSignalCatcher():
    logging.debug("model signal catcher called")
    if modeman.mode == 'NAV':
        modalFooter.base_widget.set_caption('Vi (foobar)')


# register signals and stuff 
urwid.register_signal(NbkListBox, ["nbklist insert mode", "modeChange"])
urwid.register_signal(StatusBar, ["modeChange"])


modeman = ModalManager()
nbkLW = NbkCellWalker([])
#nbkListBox = urwid.ListBox(nbkLW)
statusBar = StatusBar(edit_text = 'Vi (NAV)', selectable=True)
modalFooter = urwid.AttrMap(statusBar, 'foot')
nbkListBox = NbkListBox(nbkLW, modeman)
#view = urwid.Frame(nbkListBox, footer=modalFooter)
view = ModalFrame(nbkListBox, modeman, footer=modalFooter)

# seems smelly... 
# nbkListBox.set_parentframe(view)


urwid.connect_signal(nbkListBox, "modeChange", view.changeMode)
urwid.connect_signal(statusBar, "modeChange", view.changeMode)

# The coupling is way too tight between frame, listbox, footer 
#
# frame and listbox depend on each other
# frame needs listbox as the body 
# listbox needs to reference frame to change focus for modes. 

# possible solution: Tiered keypress filtering 
#   frame takes forwards all keypresses, except for `:`, `enter` which it uses 
#   to switch focus between listbox, footer 
# bad bads:
#   - If the nbklist has its own modal manager, then we'll have two copies of the state. 
#     messy. 
#       - could have a 'modal manager' that keeps track of what mode we're in. Then 
#         footer, frame, and listbox would all take modal manager as an input and ask it for
#         the current mode. 
#       - We could also use modal manager, and have the manager monolithically manage 
#         keypresses for frame, listbox, and footer. 


# for now, let's go with frame managing the keypresses at the top level, trickling down
# the filtered input as needed. Everyone checks with the modal manager for the current mode
# on what to do. 






# Have a mode manageer
# maintain current mode state
# if change mode to 'normal', send signal so that all the edit boxes are not selectable, but the listboxes are (for 'scrolling' through the cells)

# read the json file 
with open('census.ipynb', 'r') as f:
    ipynb = json.load(f)

cells = ipynb["cells"]

for cell in cells:
    nbkLW.append(chooseNbkCell(cell))



loop = urwid.MainLoop(view, palette, unhandled_input = show_or_exit)
loop.run()

