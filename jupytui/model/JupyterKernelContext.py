# Interface with the Jupyter kernel
import jupyter_client as jc
import nbformat
import urwid.signals
import logging


class ExecuteManager:
    """
    A "service" to execute requests and manage their lifecycle.
    """
    def __init__(self, kerClient):
        self.requests = {}
        self.kerClient = kerClient

    def executeCell(self, cell):
        r = ExecuteRequest(self.kerClient, cell)
        self.requests[r.msg_id] = r

    def __getitem__(self, key):
        return self.requests[key]

    def __setitem__(self, key, value):
        self.requests[key] = value

    def __contains__(self, item):
        return item in self.requests


class ExecuteRequest:
    def __init__(self, ctx, cell):
        self.cell = cell
        self.msg_id = ctx.execute(self.cell.asNotebookNode().source)
        self.cell.clearOutputs()

    def handleChildMessage(self, msg):
        # the execution number is in the execute_input reply
        execnum = None
        if msg["msg_type"] == 'execute_reply':

            execnum = msg['content']['execution_count']
            self.cell.lineBorder.set_title(f"In [{execnum}]")
        try:
            newOut = nbformat.v4.output_from_msg(msg)
            self.cell.appendOutput(newOut)
        except ValueError:
            # if msg_type is not acceptable (e.g. status, execute_input, etc)
            pass


class JupyterKernelContextManager:
    def __init__(self, kernelName=None):
        self.kernelName = kernelName

    def __enter__(self):
        self.jkc = JupyterKernelContext(self.kernelName)
        return self.jkc

    def __exit__(self, exceptionType, exceptionValue, traceback):
        logging.debug(f"in __exit__ jkcman")
        self.jkc.cleanup()


class JupyterKernelContext(metaclass=urwid.MetaSignals):
    signals = ["handleChildMessage"]

    def __init__(self, kernelName=None):

        self.kernelSpecManager = jc.kernelspec.KernelSpecManager()

        if kernelName is None:
            self.kerClient = None
        else:
            self.connectToKernel(kernelName)

        self.requestManager = ExecuteManager(self.kerClient)

    def cleanup(self):
        try:
            self.kerMan.shutdown_kernel()
        except AttributeError:
            pass

    def connectToKernel(self, kernelName):
        self.kerMan = jc.KernelManager(kernel_name=kernelName)
        self.kerMan.start_kernel()
        self.kerClient = self.kerMan.client()
        self.kerClient.start_channels()

    def listKernels(self):
        kspecs = self.kernelSpecManager.find_kernel_specs()
        kernelNames = kspecs.keys()
        return kernelNames

    def recvIopubMsg(self, msg):
        if "parent_header" in msg and "msg_id" in msg["parent_header"]:
            parent = msg["parent_header"]["msg_id"]
            if parent in self.requestManager:
                self.requestManager[parent].handleChildMessage(msg)

    def recvShellMsg(self, msg):
        if "parent_header" in msg and "msg_id" in msg["parent_header"]:
            parent = msg["parent_header"]["msg_id"]
            if parent in self.requestManager:
                self.requestManager[parent].handleChildMessage(msg)
