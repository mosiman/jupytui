import urwid
from jupytui.view.Cell import Cell


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
