import sys
import urwid
from model.JupyterKernelContext import JupyterKernelContextManager
import logging

# Monkeypatch: issue 386

import patch_issue_386
urwid.ListBox = patch_issue_386.ListBox

logging.basicConfig(filename='loggy.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def main():

    with JupyterKernelContextManager('python3') as jkc:
        # TODO: A bunch of setup
        palette = [
                ('fnamebox', 'black', 'white'),
                ('bg', 'black', 'dark blue'),
                ('cellFocus', 'light green', ''),
                ('foot', 'yellow', 'dark gray'),
                ('regularText', '', ''),         # so attrmap(linebox) doesn't assign to text
                ('regularLineBox', '', ''),         # so attrmap(linebox) doesn't assign to text
                ]

        txt = urwid.Text("wassssssssssuuuuuuuuuuuup")

        fill = urwid.Filler(txt, 'top')

        loop = urwid.MainLoop(
                fill, palette,
                pop_ups=True)

        loop.run()


if __name__ == "__main__":
    sys.exit(main())
