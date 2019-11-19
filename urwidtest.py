import urwid 
import logging
from urwid.monitored_list import MonitoredList, MonitoredFocusList
from urwid.listbox import ListWalkerError, ListWalker
# from pixcat import Image

from urwid.widget import WidgetMeta, Widget, BOX, FIXED, FLOW, \
    nocache_widget_render, nocache_widget_render_instance, fixed_size, \
    WidgetWrap, Divider, SolidFill, Text, CENTER, CLIP
from urwid.container import Pile, Columns
from urwid.decoration import WidgetDecoration

import json


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
        ('cellFocus', 'light green', '')
        ]

# txt = urwid.Edit(('banner', "Hello world"), multiline=True)
# map1 = urwid.AttrMap(txt, 'streak')
# boxthing = urwid.LineBox(map1)
# fill = urwid.Filler(boxthing)
# map2 = urwid.AttrMap(fill, 'bg')
# loop = urwid.MainLoop(map2, palette) 
# loop.run()


class NbkCellLineBox(urwid.LineBox):

    def __init__(self, original_widget, title="",
                 title_align="center", title_attr=None, border_attr=None,
                 tlcorner=u'┌', tline=u'─', lline=u'│',
                 trcorner=u'┐', blcorner=u'└', rline=u'│',
                 bline=u'─', brcorner=u'┘'):
        """
        Draw a line around original_widget.

        Use 'title' to set an initial title text with will be centered
        on top of the box.

        Use `title_attr` to apply a specific attribute to the title text.

        Use `title_align` to align the title to the 'left', 'right', or 'center'.
        The default is 'center'.

        Use `border_attr` to specify a attribute for the border characters.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner

        If empty string is specified for one of the lines/corners, then no
        character will be output there.  This allows for seamless use of
        adjoining LineBoxes.
        """

        if tline:
            tline = Divider(tline)
        if bline:
            bline = Divider(bline)
        if lline:
            lline = SolidFill(lline)
        if rline:
            rline = SolidFill(rline)
        tlcorner, trcorner = Text(tlcorner), Text(trcorner)
        blcorner, brcorner = Text(blcorner), Text(brcorner)

        if border_attr:
            if tline:
                tline = urwid.AttrMap(tline, border_attr)
            if bline:
                bline = urwid.AttrMap(bline, border_attr)
            if lline:
                lline = urwid.AttrMap(lline, border_attr)
            if rline:
                rline = urwid.AttrMap(rline, border_attr)
            if tlcorner:
                tlcorner = urwid.AttrMap(tlcorner, border_attr)
            if trcorner:
                trcorner = urwid.AttrMap(trcorner, border_attr)
            if blcorner:
                blcorner = urwid.AttrMap(blcorner, border_attr)
            if brcorner:
                brcorner = urwid.AttrMap(brcorner, border_attr)

        if not tline and title:
            raise ValueError('Cannot have a title when tline is empty string')

        if title_attr:
            self.title_widget = Text((title_attr, self.format_title(title)))
        else:
            self.title_widget = Text(self.format_title(title))

        if tline:
            if title_align not in ('left', 'center', 'right'):
                raise ValueError('title_align must be one of "left", "right", or "center"')
            if title_align == 'left':
                tline_widgets = [('flow', self.title_widget), tline]
            else:
                tline_widgets = [tline, ('flow', self.title_widget)]
                if title_align == 'center':
                    tline_widgets.append(tline)
            self.tline_widget = Columns(tline_widgets)
            top = Columns([
                ('fixed', 1, tlcorner),
                self.tline_widget,
                ('fixed', 1, trcorner)
            ])

        else:
            self.tline_widget = None
            top = None

        middle_widgets = []
        if lline:
            middle_widgets.append(('fixed', 1, lline))
        else:
            # Note: We need to define a fixed first widget (even if it's 0 width) so that the other
            # widgets have something to anchor onto
            middle_widgets.append(('fixed', 0, SolidFill(u"")))
        middle_widgets.append(original_widget)
        focus_col = len(middle_widgets) - 1
        if rline:
            middle_widgets.append(('fixed', 1, rline))

        middle = Columns(middle_widgets,
                box_columns=[0, 2], focus_column=focus_col)

        if bline:
            bottom = Columns([
                ('fixed', 1, blcorner), bline, ('fixed', 1, brcorner)
            ])
        else:
            bottom = None

        pile_widgets = []
        if top:
            pile_widgets.append(('flow', top))
        pile_widgets.append(middle)
        focus_pos = len(pile_widgets) - 1
        if bottom:
            pile_widgets.append(('flow', bottom))
        pile = Pile(pile_widgets, focus_item=focus_pos)

        WidgetDecoration.__init__(self, original_widget)
        WidgetWrap.__init__(self, pile)

    def set_title_attr(self, attrname):
        title = self.title_widget.text
        self.title_widget = urwid.Text((attrname, self.format_title(title)))
    def set_focus_attr(self):
        title = self.title_widget.text
        self.__init__(self._get_original_widget(), title=title, border_attr='cellFocus')
    def set_nofocus_attr(self):
        title = self.title_widget.text
        self.__init__(self._get_original_widget(), title=title)
    def rerender(self):
        size = (3,)
        title = self.title_widget.text
        # self.title_widget = urwid.Text(('cellFocus', self.format_title(title)))
        # self.render(size)
        self.__init__(self._get_original_widget(), title = self.title_widget.text,
                        border_attr='cellFocus')


class ModelNavListWalker(MonitoredList, ListWalker):
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
            raise ListWalkerError("SimpleListWalker expecting list like object, got: %r"%(contents,))
        MonitoredList.__init__(self, contents)
        self.focus = 0
        self.prev_focus = 0

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
        ListWalker._modified(self)

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

        self.prev_focus = self.focus
        self.focus = position
        self._modified()

        # try to make the selected box more obvious
        self.contents[self.prev_focus].set_nofocus_attr()
        self.contents[self.focus].set_focus_attr()

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

def add_editbox(key):
    if key in ('q', 'Q'):
        # raise urwid.ExitMainLoop()
        modalLW.append(urwid.LineBox(urwid.Text("sup2")))
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
    if cell["cell_type"] == 'markdown':
        return NbkCellMkdn(''.join(cell["source"]))
    elif cell["cell_type"] == 'code':
        # process the output 
        out = handleCodeOutput(cell["outputs"])
        return NbkCellCode(''.join(cell["source"]), out)
    elif cell["cell_type"] == 'raw':
        return NbkCellRaw(''.join(cell["source"]))


class NbkCell(urwid.WidgetWrap):
    def __init__(self, src):
        #self.cell = urwid.LineBox(urwid.Edit(src, multiline=True))
        self.cell = NbkCellLineBox(urwid.Edit(src, multiline=True))
        urwid.WidgetWrap.__init__(self, self.cell)
    def set_title(self, titletext):
        self.cell.set_title(titletext)
    def set_focus_attr(self):
        self.cell.set_focus_attr()
    def set_nofocus_attr(self):
        self.cell.set_nofocus_attr()
    def rerender(self):
        self.cell.rerender()

class NbkCellRaw(NbkCell):
    def __init__(self, src):
        super().__init__(src)

# Eventually, need to have modes for 'in focus' or 'not in focus' / 
#   'dont render images', 'render images' for using pixcat to display
#   markdown images
class NbkCellMkdn(NbkCell):
    def __init__(self, src):
        super().__init__(src)
    
class NbkCellCode(NbkCell):
    def __init__(self, src, out):
        super().__init__(src)
        self.outCell = urwid.Text(out)
        # put them in a pile 
        stacked = urwid.Pile([self.cell, self.outCell])
        urwid.WidgetWrap.__init__(self, stacked) 

# loop = urwid.MainLoop(urwid.ListBox(urwid.SimpleFocusListWalker(body)), unhandled_input = add_editbox)

simpleLW = urwid.SimpleFocusListWalker([])

modalLW = ModelNavListWalker([])
testlistbox = urwid.ListBox(modalLW)

# Have a mode manageer
# maintain current mode state
# if change mode to 'normal', send signal so that all the edit boxes are not selectable, but the listboxes are (for 'scrolling' through the cells)

# read the json file 
with open('census.ipynb', 'r') as f:
    ipynb = json.load(f)

cells = ipynb["cells"]

#modalLW.append(urwid.AttrMap(urwid.LineBox(urwid.Text('asdfasdf')), 'cellFocus'))
#modalLW.append(NbkCellLineBox(urwid.Text('asdfasdf'), title='foobar', title_align='left', border_attr='cellFocus'))

for cell in cells:
    modalLW.append(chooseNbkCell(cell))



loop = urwid.MainLoop(testlistbox, palette, unhandled_input = show_or_exit)
loop.run()

