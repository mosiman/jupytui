import urwid

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
        # Originally, I wanted to have walker generate Cell objects on the fly 
        # (i.e. whenever __getitem__ is called), but turns out there is a bit of a scope
        # issue. 
        # If instead of __getitem__ returning `self.cells[pos]` (list of Cells)
        # it returned `Cell(self.nbk.cells[pos])` the listbox would not update the view.
        # Now, I need to maintain a separate list of cell objects that should be synced
        # back to the notebook object.
        # In terms of syncing:
        #   - When the edit box's content has changed, there is no need to sync with 
        #     the notebook until we 'save'. 
        #   - If the cell is executed, we should save the results into notebook, and then
        #     remake the Cell object with the appropriate things.
        # TODO: Have NotebookWalker subclass SimpleListWalker (or SimpleFocusListWalker)
        #       It will be more easily maintainable, and easier to read.
        #       Should just be the subclass, plus a notebook object and some sync functions.
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

        if 'execution_count' in cell.keys():
            srcTitleText = 'In [' + str(cell.execution_count) + ']'
        else:
            srcTitleText = ''

        # TODO: this will change when I implement syntax highlighting
        self.editbox = urwid.AttrMap(SelectableEdit(edit_text=self.source, allow_tab=True, multiline=True), 'regularText')
        lineBorder = urwid.LineBox(self.editbox, title=srcTitleText, title_attr='regularText', title_align='left')
        self.srcWidget=urwid.AttrMap(lineBorder, 'regularLineBox', focus_map='cellFocus')
        self.outwidgets = handleCodeOutput(cell["outputs"]) if "outputs" in cell.keys() else []

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
        # srcWidget = urwid.AttrMap(urwid.LineBox(self.editbox), 'regularLineBox', focus_map='cellFocus')
        # TODO implement cell output later: need to hide html/img/etc types
        # Add the cell outputs to pile

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
