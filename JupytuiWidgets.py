import urwid
import heapq
import time
import select
import jupyter_client
import nbformat
import logging
import zmq

class JCEventLoop(urwid.SelectEventLoop, metaclass=urwid.MetaSignals):
    """
    A `urwid.SelectEventLoop` with loop modified to call signals if a message is available on one of the kernel's channels.
    Also, basically the same as `https://gist.github.com/sphaero/8225315`
        TODO: proper attribution
    """
    signals = ["iopubMsg", "shellMsg", "stdinMsg"]
    def __init__(self, kerClient = None):
        self.kerClient = kerClient
        self.zmqPoller = zmq.Poller()
        super().__init__()

    def watch_channel(self, soc: zmq.sugar.socket.Socket, callback):
        self._watch_files[soc] = callback
        self.zmqPoller.register(soc, zmq.POLLIN)
        return soc

    def _check_msg(self):
        """
        Checks messages on iopub, shell, stdin channels
        """
        if self.kerClient:
            if self.kerClient.iopub_channel.msg_ready():
                logging.debug(f"iopub channel has message ready")
                msg = self.kerClient.get_iopub_msg(0)
                urwid.emit_signal(self, "iopubMsg", msg)
            if self.kerClient.shell_channel.msg_ready():
                logging.debug(f"shell channel has message ready")
            if self.kerClient.stdin_channel.msg_ready():
                logging.debug(f"stdin channel has message ready")

    def _loop(self):
        """
        A single iteration of the event loop. Modified from SelectEventLoop to check for kernel messages. Inspiration from github.com/wackywendell and their `ipyurwid repository.
        """
        fds = list(self._watch_files.keys())
        if self._alarms or self._did_something:
            if self._alarms:
                tm = self._alarms[0][0]
                timeout = max(0, tm - time.time())
            if self._did_something and (not self._alarms or
                    (self._alarms and timeout > 0)):
                timeout = 0
                tm = 'idle'
            items = dict(self.zmqPoller.poll(timeout))
            #ready, w, err = select.select(fds, [], fds, timeout)
        else:
            tm = None
            items = dict(self.zmqPoller.poll())
            #ready, w, err = select.select(fds, [], fds)

        if not items:
            if tm == 'idle':
                self._entering_idle()
                self._did_something = False
            elif tm is not None:
                # must have been a timeout
                # tm, tie_break, alarm_callback = heapq.heappop(self._alarms)
                tm, alarm_callback = self._alarms.pop(0)
                alarm_callback()
                self._did_something = True

        for fd, ev in items.items():
            self._watch_files[fd]()
            self._did_something = True


def handleCodeOutput(outputs):
    """
    Takes the outputs of a cell, returns a list of appropriate widgets to be used in a Pile
    """
    outwidgets = []
    for output in outputs:
        if output["output_type"] == 'stream':
            lines = output["text"].split('\n')
            outwidgets.append(urwid.Text(output["text"]))
        elif output["output_type"] == 'display_data':
            widg = NiceButton('<< Some display data >>', on_press=None)
            outwidgets.append(urwid.AttrMap(widg, 'regularText', 'cellFocus'))
        elif output["output_type"] == 'execute_result':
            data = output["data"]
            for datatype in data.keys():
                if datatype == "text/plain":
                    outwidgets.append(urwid.Text(data['text/plain']))
                else:
                    widg = NiceButton(f'<< Some {datatype} >>', on_press=None)
                    outwidgets.append(urwid.AttrMap(widg, 'regularText', 'cellFocus'))
                outwidgets.append(urwid.Text(''))
        outwidgets.append(urwid.Text(''))
    return outwidgets

class ButtonLabel(urwid.SelectableIcon):
    '''
    use Drunken Master's trick to move the cursor out of view
    See the SO answer by Michael Palmer, https://stackoverflow.com/a/44682928
    '''
    def set_text(self, label):
        '''
        set_text is invoked by Button.set_label
        '''
        self.__super.set_text(label)
        self._cursor_position = len(label) + 1


class NiceButton(urwid.Button):
    '''
    - override __init__ to use our ButtonLabel instead of urwid.SelectableIcon

    - make button_left and button_right plain strings and variable width -
      any string, including an empty string, can be set and displayed

    - otherwise, we leave Button behaviour unchanged

    Courtesy of Michael Palmer, https://stackoverflow.com/a/44682928
    '''
    button_left = ""
    button_right = ""

    def __init__(self, label, on_press=None, user_data=None):
        self._label = ButtonLabel("")
        cols = urwid.Columns([
            ('fixed', len(self.button_left), urwid.Text(self.button_left)),
            self._label,
            ('fixed', len(self.button_right), urwid.Text(self.button_right))],
            dividechars=1)
        super(urwid.Button, self).__init__(cols)

        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

        self.set_label(label)

class SelectableEdit(urwid.Edit):
    """
    Extension of urwid.Edit. Allows us to target more precisely the editboxes that shouldn't be selectable.
    """
    pass


class NotebookWalker(urwid.ListWalker):
    def __init__(self, nbk):
        self.nbk = nbk
        self.cells = list(map(Cell, self.nbk.cells))
        self.focus = 0

    def _modified(self):
        if self.focus >= len(self):
            self.focus = max(0, len(self)-1)
        urwid.ListWalker._modified(self)

    def __len__(self):
        return len(self.cells)

    def set_focus(self, position):
        """Set focus position."""
        try:
            if position < 0 or position >= len(self):
                raise ValueError
        except (TypeError, ValueError):
            raise IndexError("No widget at position %s" % (position,))
        self.focus = position
        self._modified()

    def __getitem__(self, position):
        return self.cells[position]
    
    def next_position(self, position):
        """
        Return position after start_from.
        """
        if len(self) - 1 <= position:
            raise IndexError
        return position + 1

    def prev_position(self, position):
        """
        Return position before start_from.
        """
        if position <= 0:
            raise IndexError
        return position - 1

    def positions(self, reverse=False):
        """
        Optional method for returning an iterable of positions.
        """
        if reverse:
            return range(len(self) - 1, -1, -1)
        return range(len(self))

class Cell(urwid.Pile):
    def __init__(self, cell):
        self.cell_type = cell.cell_type
        self.metadata = cell.metadata
        self.source = cell.source # source is not edited when editbox is, need explicit sync
        self.execution_count = None

        if 'outputs' in cell.keys():
            self.outputs = cell["outputs"]

        if 'execution_count' in cell.keys():
            self.execution_count = cell.execution_count
            srcTitleText = 'In [' + str(self.execution_count) + ']'
        else:
            srcTitleText = ''

        # TODO: this will change when I implement syntax highlighting
        self.editbox = urwid.AttrMap(SelectableEdit(edit_text=self.source, allow_tab=True, multiline=True), 'regularText')
        lineBorder = urwid.LineBox(self.editbox, title=srcTitleText, title_attr='regularText', title_align='left')
        self.srcWidget=urwid.AttrMap(lineBorder, 'regularLineBox', focus_map='cellFocus')
        self.outwidgets = handleCodeOutput(self.outputs) if "outputs" in cell.keys() else []

        super().__init__([self.srcWidget, *self.outwidgets])

    def selectable(self):
        myWidgetsSelectable = list(map(lambda x: x[0].selectable(), self.contents))
        return any(myWidgetsSelectable)
    def keypress(self, size, key):
        keyResult = super().keypress(size, key)
        if keyResult:
            return keyResult
    def get_focus(self):
        if not self.contents:
            return None
        return self.contents[self.focus_position][0].base_widget
    focus = property(get_focus,
        doc="the base child widget in focus or None when Pile is empty")

    def asNotebookNode(self):
        """
        Return this cell as a notebook node
        """
        src = self.editbox.base_widget.get_edit_text()
        if self.cell_type == 'code':
            nbkCell = nbformat.v4.new_code_cell(source = src)
            # NOTE cell.outputs should be up to date
            # i.e., update it when we get the appropriate IOPub msg via nbformat.v4.output_from_msg
            nbkCell.execution_count = self.execution_count
            nbkCell.outputs = self.outputs
        elif self.cell_type == 'markdown':
            nbkCell = nbformat.v4.new_markdown_cell(source = src)
        elif self.cell_type == 'raw':
            nbkCell = nbformat.v4.new_raw_cell(source = src)
        else:
            raise ValueError

        return nbkCell




class CellV1(urwid.WidgetWrap):
    """
    Cells display these things in a vertical list (a pile)
        - A editable text box for the source
        - A series of texts for the output
    This class' constructor takes a `nbformat.notebooknode.NotebookNode`, for example

    ```
    nbk = nbformat.read('notebook.ipynb', nbformat.NO_CONVERT)

    c = Cell(nbk.cells[0])
    """

    def __init__(self, cell):
        self.cell_type = cell.cell_type
        self.metadata = cell.metadata
        self.source = cell.source # source is not edited when editbox is, need explicit sync

        if 'execution_count' in cell.keys():
            srcTitleText = 'In [' + str(cell.execution_count) + ']'
        else:
            srcTitleText = ''

        # TODO: this will change when I implement syntax highlighting
        self.editbox = urwid.AttrMap(SelectableEdit(edit_text=self.source, allow_tab=True, multiline=True), 'regularText')
        lineBorder = urwid.LineBox(self.editbox, title=srcTitleText, title_attr='regularText', title_align='left')
        srcWidget=urwid.AttrMap(lineBorder, 'regularLineBox', focus_map='cellFocus')

        outwidgets = handleCodeOutput(cell["outputs"]) if "outputs" in cell.keys() else []

        display_widget = urwid.Pile([srcWidget, *outwidgets])

        urwid.WidgetWrap.__init__(self, display_widget)

class PopUpDialog(urwid.WidgetWrap):
    signals = ['close']
    def __init__(self, text):
        close_button = urwid.Button("OK")
        urwid.connect_signal(close_button, 'click',
            lambda button:self._emit("close"))
        pile = urwid.Pile([urwid.Text(text), close_button])
        fill = urwid.Filler(pile)
        lb = urwid.LineBox(fill)
        self.__super.__init__(urwid.AttrWrap(lb, 'popbg'))

class PopUpListSelectText(urwid.WidgetWrap):
    signals = ['close']
    def __init__(self, title, widgList):
        body = [urwid.Text(title), urwid.Divider()]
        for widg in widgList:
            button = NiceButton(widg.text)
            urwid.connect_signal(button, 'click', lambda button: urwid.emit_signal(self, "close", widg))
            body.append(urwid.AttrMap(button, None, focus_map='cellFocus'))
        close_button = urwid.Button("Close")
        urwid.connect_signal(close_button, 'click', lambda button: urwid.emit_signal(self, "close", urwid.Text("")))
        body.append(urwid.Divider())
        body.append(close_button)
        pile = urwid.Pile(body)
        fill = urwid.Filler(pile)
        lb = urwid.LineBox(fill)
        self.__super.__init__(urwid.AttrWrap(lb, 'popbg'))



