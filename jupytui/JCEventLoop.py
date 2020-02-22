import urwid
import time
import zmq
import zmq_loop.urwid_zmq_event_loop


class JCEventLoop(urwid.SelectEventLoop, metaclass=urwid.MetaSignals):
    """
    A `urwid.SelectEventLoop` with loop modified to call signals if a message
    is available on one of the kernel's channels. Also, basically the same as
    `https://gist.github.com/sphaero/8225315`
        TODO: proper attribution
    """
    signals = ["iopubMsg", "shellMsg", "stdinMsg"]

    def __init__(self, kerClient=None):
        self.kerClient = kerClient
        self.zmqPoller = zmq.Poller()
        super().__init__()

    def watch_channel(self, soc: zmq.sugar.socket.Socket, callback):
        self._watch_files[soc] = callback
        self.zmqPoller.register(soc, zmq.POLLIN)
        return soc

    def _check_msg(self):
        """
        Checks messages on iopub, shell, stdin channels
        """
        if self.kerClient:
            if self.kerClient.iopub_channel.msg_ready():
                msg = self.kerClient.get_iopub_msg(0)
                urwid.emit_signal(self, "iopubMsg", msg)
            if self.kerClient.shell_channel.msg_ready():
                pass
            if self.kerClient.stdin_channel.msg_ready():
                pass

    def _loop(self):
        """
        A single iteration of the event loop. Modified from SelectEventLoop to
        check for kernel messages. Inspiration from github.com/wackywendell and
        their `ipyurwid repository.
        """
        fds = list(self._watch_files.keys())
        if self._alarms or self._did_something:
            if self._alarms:
                tm = self._alarms[0][0]
                timeout = max(0, tm - time.time())
            if self._did_something and (
                    not self._alarms or
                    (self._alarms and timeout > 0)):
                timeout = 0
                tm = 'idle'
            items = dict(self.zmqPoller.poll(timeout))
        else:
            tm = None
            items = dict(self.zmqPoller.poll())

        if not items:
            if tm == 'idle':
                self._entering_idle()
                self._did_something = False
            elif tm is not None:
                # must have been a timeout
                # tm, tie_break, alarm_callback = heapq.heappop(self._alarms)
                tm, alarm_callback = self._alarms.pop(0)
                alarm_callback()
                self._did_something = True

        for fd, ev in items.items():
            self._watch_files[fd]()
            self._did_something = True
