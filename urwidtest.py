import urwid 

import json

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()
    txt.set_edit_text(key)

palette = [
        ('banner', 'black', 'light gray'),
        ('streak', 'black', 'dark red'),
        ('bg', 'black', 'dark blue')
        ]

# txt = urwid.Edit(('banner', "Hello world"), multiline=True)
# map1 = urwid.AttrMap(txt, 'streak')
# boxthing = urwid.LineBox(map1)
# fill = urwid.Filler(boxthing)
# map2 = urwid.AttrMap(fill, 'bg')
# loop = urwid.MainLoop(map2, palette) 
# loop.run()


class NbkCellWalker(urwid.ListWalker):
    def __init__(self):
        self.focus = (0,1)
        self.cells = []

    def _get_at_pos(self, pos):
        if pos[1] == 1 and len(self.cells) == 0:
            return urwid.LineBox(urwid.Text("fuck")), pos
        else:
            return self.cells[pos], pos

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        a,b = start_from 
        focus = a,b+1
        return self._get_at_pos(focus)

    def get_prev(self, start_from):
        a,b = start_from 
        if b == 1:
            focus = start_from
        else:
            focus = a,b-1
        return self._get_at_pos(focus)
    



body0 = [
    urwid.LineBox(urwid.Edit("sup1", multiline=True)),
    urwid.LineBox(urwid.Edit("sup1", multiline=True)),
    urwid.LineBox(urwid.Edit("sup1", multiline=True)),
    urwid.LineBox(urwid.Edit("sup1", multiline=True)),
    urwid.LineBox(urwid.Edit("sup1", multiline=True)),
    urwid.LineBox(urwid.Edit("sup1", multiline=True))
]

body = [
    urwid.LineBox(urwid.Text("sup1")),
    urwid.LineBox(urwid.Text("sup1")),
    urwid.LineBox(urwid.Text("sup1")),
    urwid.LineBox(urwid.Text("sup1")),
    urwid.LineBox(urwid.Text("sup1")),
    urwid.LineBox(urwid.Text("sup1"))
]

def add_editbox(key):
    if key in ('q', 'Q'):
        # raise urwid.ExitMainLoop()
        simpleLW.append(urwid.LineBox(urwid.Text("sup2")))
    return True


# loop = urwid.MainLoop(urwid.ListBox(urwid.SimpleFocusListWalker(body)), unhandled_input = add_editbox)

NbkCellList = urwid.ListBox(NbkCellWalker())

simpleLW = urwid.SimpleFocusListWalker([])
testlistbox = urwid.ListBox(simpleLW)

# read the json file 
with open('Transformation2D.ipynb', 'r') as f:
    ipynb = json.load(f)

cells = ipynb["cells"][0:5]

for cell in cells:
    src = ''.join(cell["source"])
    simpleLW.append(urwid.LineBox(urwid.Edit(src, multiline=True)))


loop = urwid.MainLoop(testlistbox, unhandled_input = add_editbox)
loop.run()

