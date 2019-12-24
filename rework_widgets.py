

import logging

import urwid


# make a custom listwalker that walks through nbformat.notebooknode object
# - uses cell to display the widget
# - Any changes made should be made directly to self.nbk


# BUG:  want to see what is missing from SimpleListWalker implementation from NotebookWalker
#       that causes strange issues with edit boxes not accepting input. 
#       - PgUp/Dn sometimes work
#       - Down arrow works to go to next editbox
#       - Up arrow doesn't work unless text fits on one line?
#       - Seems like an issue with keypress filtering. Not sure where.

class CloneWalker(urwid.ListWalker):
    def __init__(self, contents):
        """
        contents -- list to copy into this object

        This class inherits :class:`MonitoredList` which means
        it can be treated as a list.

        Changes made to this object (when it is treated as a list) are
        detected automatically and will cause ListBox objects using
        this list walker to be updated.
        """
        if not getattr(contents, '__getitem__', None):
            raise urwid.ListWalkerError("SimpleListWalker expecting list like object, got: %r"%(contents,))
        # MonitoredList.__init__(self, contents)
        self.focus = 0

    def _get_contents(self):
        """
        Return self.

        Provides compatibility with old SimpleListWalker class.
        """
        return self
    contents = property(_get_contents)

    def _modified(self):
        if self.focus >= len(self):
            self.focus = max(0, len(self)-1)
        urwid.ListWalker._modified(self)

    def set_modified_callback(self, callback):
        """
        This function inherited from MonitoredList is not
        implemented in SimpleListWalker.

        Use connect_signal(list_walker, "modified", ...) instead.
        """
        raise NotImplementedError('Use connect_signal('
            'list_walker, "modified", ...) instead.')

    def set_focus(self, position):
        """Set focus position."""
        try:
            if position < 0 or position >= len(self):
                raise ValueError
        except (TypeError, ValueError):
            raise IndexError("No widget at position %s" % (position,))
        self.focus = position
        self._modified()

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

class NotebookWalkerV1(urwid.ListWalker):
    def __init__(self, nbk):
        self.nbk = nbk
        self.focus = 0

    def _modified(self):
        if self.focus >= len(self):
            self.focus = max(0, len(self)-1)
        logging.debug(f"NbkWalkerV1 is modified")
        urwid.ListWalker._modified(self)

    def __len__(self):
        return len(self.nbk.cells)

    def set_focus(self, position):
        """Set focus position."""
        try:
            if position < 0 or position >= len(self):
                raise ValueError
        except (TypeError, ValueError):
            raise IndexError("No widget at position %s" % (position,))
        self.focus = position
        self._modified()

    def get_focus(self):
        return Cell(self.nbk.cells[self.focus]), self.focus
    
    def get_next(self, start_from):
        """
        Return position after start_from.
        """
        position = start_from + 1
        if len(self) - 1 <= position:
            return None, None
        return Cell(self.nbk.cells[position]), position

    def get_prev(self, start_from):
        """
        Return position before start_from.
        """
        position = start_from - 1
        if position <= 0:
            return None, None
        return Cell(self.nbk.cells[position]), position

    def positions(self, reverse=False):
        """
        Optional method for returning an iterable of positions.
        """
        if reverse:
            return range(len(self) - 1, -1, -1)
        return range(len(self))


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
        srctxt = cell.source

        # wrap edit box with attribute, so that attrmap(linebox) doesn't assign to edit box
        editbox = urwid.AttrMap(urwid.Edit(edit_text=srctxt), 'regularText')
        # wrap linebox with attr, when focused give it cellFocus attribute
        srcWidget = urwid.AttrMap(urwid.LineBox(editbox), 'regularLineBox', focus_map='cellFocus')
        # TODO implement cell output later: need to hide html/img/etc types
        # Add the cell outputs to pile
        display_widget = urwid.Pile([srcWidget])

        urwid.WidgetWrap.__init__(self, display_widget)
