# Represents an IPython notebook, along with various contextual bits
# e.g., file name, IO methods.

import nbformat


class IPythonContextException(Exception):
    pass


class IPythonVersionConflictException(IPythonContextException):
    pass


class IPythonContext:
    def __init__(self, fname=""):
        self.fname = fname

        if not self.fname:
            # Create a new notebook, newest version
            self.nbk = nbformat.v4.new_notebook()
        else:
            # Keep the original version, until asked to save.
            self.nbk = nbformat.read(fname, nbformat.NO_CONVERT)

    def updateNotebookRepresentation(self, nbk):
        self.nbk = nbk

    def loadFromNbkWalker(self, nbkWalker, forceNewVersion=False):
        if self.nbk.nbformat != 4 and not forceNewVersion:
            raise IPythonVersionConflictException()
        newNbk = nbformat.v4.new_notebook()
        newNbk.metadata = nbkWalker.nbk.metadata

        for cell in nbkWalker.cells:
            newNbk.cells.append(cell.asNotebookNode())
        return newNbk

    def save(self, fname=None):
        if not (fname or self.fname):
            raise IPythonContextException("Save requires filename")
        if fname:
            nbformat.write(self.nbk, fname)
        else:
            nbformat.write(self.nbk, self.fname)
