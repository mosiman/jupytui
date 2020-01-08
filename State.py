import urwid

# get rid of later
import logging
import nbformat

from JupytuiWidgets import SelectableEdit

def commandParse(command, cmdbox):
    """
    Parses the text in cmdbox. Returns nothing if all is good, returns an error message otherwise.
    As input, takes the command text and a reference to the commandbox.
    """
    cmdsplit = command.split(' ')
    fn = cmdsplit[0]
    arg = ' '.join(command.split(' ')[1:]) if len(cmdsplit) > 1 else None

    if fn == '':
        return 'no command'
    if fn == 'w':
        logging.debug(f'command: writing to file {arg}')
    if fn == 'o':
        if arg:
            logging.debug(f'command: opening file {arg}')
            urwid.emit_signal(cmdbox, 'cmdOpen', arg)
        else:
            return 'no filename specified for opening'
    return 'command not recognized'

class StateBase:
    def __init__(self, context):
        self.context = context
    def keypress(self, size, key):
        pass

class EditState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        SelectableEdit._selectable = True
        self.context.cmdbox.set_caption('')
        self.context.cmdbox.edit_text = "(EDIT)"
        # If focus happens to be on a button, we need to force the focus to be on the source.
        # TODO this kinda smells tbh, should be accessible more directly from StatefulFrame
        # logging.debug(f'testtest {self.context.listbox.focus._w}')
        # logging.debug(f'focus pos: {self.context.listbox.focus._w.focus_position}')
        # self.context.listbox.focus._w.focus_position = 0
    def keypress(self, size, key):
        logging.debug(f'keypress caught by EditState: {key}')
        if key in ['esc']:
            # Switch to Nav state
            self.context._state = NavState(self.context)
            return
        if key in ['f4']:
            logging.debug(f'focuspath: {self.context.get_focus_widgets()}')
        if key in ['f7']:
            logging.debug(f'edit selectable? {self.context.listbox.body[0].editbox.selectable()}')
        if key in ['f8']:
            logging.debug(f'Cell focus: {self.context.listbox.body[0].focus}')
        self.context.superkeypress(size, key)

class CmdState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        self.context.cmdbox.set_caption(':')
        self.context.cmdbox.edit_text = ''
        self.context.focus_part = 'footer'

    def keypress(self, size, key):
        # Avoid all unless it's 'enter'
        logging.debug(f'key press caught by CmdState: {key}')
        if key in ['enter']:
            logging.debug(f'cmd is {self.context.cmdbox.get_edit_text()}')
            cmdResult = commandParse(self.context.cmdbox.get_edit_text(), self.context.cmdbox)

            if self.context.cmdbox.get_edit_text() == 'foobar':
                logging.debug('sup')
                self.context.listbox.body.restore_cells()

            if not cmdResult:
                self.context.focus_part = 'body'
                self.context._state = NavState(self.context)
            else:
                if cmdResult == 'no command':
                    # self.context.listbox.body.cells.pop(0)
                    
                    # nbk = nbformat.read('census.ipynb', nbformat.NO_CONVERT)
                    # self.context.listbox.body.change_notebook(nbk)

                    self.context.listbox.body.delete_all_cells()

                    self.context.focus_part = 'body'
                    self.context._state = NavState(self.context)
                else:
                    self.context._state = CmdState(self.context)
        keyResult = self.context.superkeypress(size, key)
        if keyResult:
            return keyResult

class NavState(StateBase):
    def __init__(self, context):
        super().__init__(context)
        # Set edits to be not selectable in Nav mode
        SelectableEdit._selectable = False
        self.context.cmdbox.set_caption('')
        self.context.cmdbox.edit_text = "(NAV)"
        self.context.focus_part = 'body'
    def keypress(self, size, key):
        logging.debug(f'key press caught by NavState: {key}')
        if key in ['j', 'k', 'g', 'G']:
            currentFocusPos = self.context.listbox.focus_position
            if key == 'j':
                try:
                    nextFocusPos = self.context.listbox.body.next_position(currentFocusPos)
                except IndexError:
                    nextFocusPos = currentFocusPos
            if key == 'k':
                try:
                    nextFocusPos = self.context.listbox.body.prev_position(currentFocusPos)
                except IndexError:
                    nextFocusPos = currentFocusPos
            if key == 'g':
                pass
            if key == 'G':
                pass
            self.context.listbox.set_focus(nextFocusPos)
        if key in ['i', 'a']:
            # Switch to Edit state
            self.context._state = EditState(self.context)
            return
        if key in [':']:
            self.context._state = CmdState(self.context)
        return key

class StatefulFrame(urwid.Frame):

    def __init__(self, body, header=None, footer=None, focus_part='body'):
        super().__init__(body, header=header, footer=footer, focus_part=focus_part)
        # initial state
        self.cmdbox = self.footer[1]
        self.listbox = self.body
        self._state = NavState(self)

    def keypress(self, size, key):
        keyResult = self._state.keypress(size, key)
        if keyResult:
            return keyResult

    def superkeypress(self, size, key):
        keyResult = super().keypress(size, key)
        if keyResult:
            return keyResult
