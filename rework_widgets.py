

import logging

import urwid

class SelectableEdit(urwid.Edit):
    """
    Extension of urwid.Edit, allowing to be selectable or not selectable.
    """
    def selectable(self):
        return self._selectable


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

class Cell(urwid.WidgetWrap):
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

        # wrap edit box with attribute, so that attrmap(linebox) doesn't assign to edit box
        # TODO: this will change when I implement syntax highlighting
        self.editbox = urwid.AttrMap(SelectableEdit(edit_text=self.source), 'regularText')
        # wrap linebox with attr, when focused give it cellFocus attribute
        srcWidget = urwid.AttrMap(urwid.LineBox(self.editbox), 'regularLineBox', focus_map='cellFocus')
        # TODO implement cell output later: need to hide html/img/etc types
        # Add the cell outputs to pile
        display_widget = urwid.Pile([srcWidget])

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
