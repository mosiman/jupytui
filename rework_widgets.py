



import urwid


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
        # TODO implement cell output later: need to hide html/img/etc types

        # wrap edit box with attribute, so that attrmap(linebox) doesn't assign to edit box
        editbox = urwid.AttrMap(urwid.Edit(edit_text=srctxt), 'regularText')
        #srcWidget = urwid.LineBox(urwid.Text(('regularText', srctxt)))
        srcWidget = urwid.AttrMap(urwid.LineBox(editbox), 'regularLineBox', focus_map='cellFocus')
        display_widget = urwid.Pile([srcWidget])

        urwid.WidgetWrap.__init__(self, display_widget)
