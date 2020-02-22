import urwid
import nbformat


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
        self.lineBorder = urwid.LineBox(self.editbox, title=srcTitleText, title_attr='regularText', title_align='left')
        self.srcWidget=urwid.AttrMap(self.lineBorder, 'regularLineBox', focus_map='cellFocus')
        self.outwidgets = handleCodeOutput(self.outputs) if "outputs" in cell.keys() else []

        super().__init__([self.srcWidget, *self.outwidgets])

    def appendOutput(self, out):
        self.outputs.append(out)
        self.contents.append((handleCodeOutput([out])[0], self.options()))

    def clearOutputs(self):
        self.outputs.clear()
        del self.contents[1:]

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
    focus = property(
            get_focus,
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
