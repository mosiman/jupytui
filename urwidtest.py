import urwid 


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
        self.focus = (0, 1)

    def _get_at_pos(self, pos):
        return urwid.LineBox(urwid.Edit(f"pos {pos}", multiline=True)), pos

    def get_focus(self):
        return self._get_at_pos(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, start_from):
        a,b = start_from 
        focus = a, b+1
        return self._get_at_pos(focus)

    def get_prev(self, start_from):
        a,b = start_from 
        focus = a, b-1
        return self._get_at_pos(focus)
    



body = [
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
        body.append(urwid.LineBox(urwid.Text("sup2")))

    return True


# loop = urwid.MainLoop(urwid.ListBox(urwid.SimpleFocusListWalker(body)), unhandled_input = add_editbox)
loop = urwid.MainLoop(urwid.ListBox(NbkCellWalker()))
loop.run()

