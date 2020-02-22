import urwid
from jupytui.view.NiceButton import NiceButton

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
