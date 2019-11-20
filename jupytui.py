import urwid 
import logging
# from pixcat import Image


import json

from NbkUrwid import NbkCellLineBox, NbkCellWalker, NbkListBox, \
                     NbkEditBox, \
                     NbkCellRaw, NbkCellMkdn, NbkCellCode

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
        ('cellFocus', 'light green', ''),
        ('foot', 'yellow', 'dark gray')
        ]



def add_editbox(key):
    if key in ('q', 'Q'):
        # raise urwid.ExitMainLoop()
        nbkLW.append(urwid.LineBox(urwid.Text("sup2")))
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
    
    if 'execution_count' in cell:
        runNum = cell['execution_count']
        logging.debug(f"execution count found: {cell['execution_count']}")
    else:
        runNum = ''


    if cell["cell_type"] == 'markdown':
        return NbkCellMkdn(''.join(cell["source"]), runNum=runNum)
    elif cell["cell_type"] == 'code':
        # process the output 
        out = handleCodeOutput(cell["outputs"])
        return NbkCellCode(''.join(cell["source"]), out, runNum=runNum)
    elif cell["cell_type"] == 'raw':
        return NbkCellRaw(''.join(cell["source"]), runNum=runNum)


simpleLW = urwid.SimpleFocusListWalker([])

nbkLW = NbkCellWalker([])
#nbkListBox = urwid.ListBox(nbkLW)
modalFooter = urwid.AttrMap(urwid.Text('Vi (NAV)'), 'foot')
nbkListBox = NbkListBox(nbkLW, footer=modalFooter)
view = urwid.Frame(nbkListBox, footer=modalFooter)

# Have a mode manageer
# maintain current mode state
# if change mode to 'normal', send signal so that all the edit boxes are not selectable, but the listboxes are (for 'scrolling' through the cells)

# read the json file 
with open('census.ipynb', 'r') as f:
    ipynb = json.load(f)

cells = ipynb["cells"]

for cell in cells:
    nbkLW.append(chooseNbkCell(cell))



loop = urwid.MainLoop(view, palette, unhandled_input = show_or_exit)
loop.run()

