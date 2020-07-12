import sys
import threading
import queue

from PySide2.QtCore import QTimer


class StdinListener:
    """ 
    1) runs a thread that reads stdin in parallel and puts any data read into a queue
    2) runs a timer in gui thread that periodically checks the queue
       and if theres some data -> calls the callback with line by line data from the queue
       on first run calls callback with "start" as a notification about data having started arriving on stdin
    """

    def __init__(self, callback, check_interval_ms=1000):
        self.callback = callback
        self.read_started = False

        self.timer = QTimer()
        self.timeout = check_interval_ms
        self.timer.timeout.connect(self.check_queue)

        self.stdin_line_queue = queue.Queue()
        self.parallel_reader = threading.Thread(
            target=self.parallel_read_stdin, args=(self.stdin_line_queue,))

        self.parallel_reader.setDaemon(True)  # kill when main pocess exits

    def parallel_read_stdin(self, q: queue):
        """read line from stdin in parallel thread and put line read into the queue"""
        for line in sys.stdin:  # this is blocked until data in stdin available
            self.stdin_line_queue.put(line.rstrip())

    def start_paused(self):
        """start timer and start the thread"""
        self.paused = True
        self.timer.start(self.timeout)
        self.parallel_reader.start()

    def check_queue(self):
        """
        check if any line in queue and call the callback with one line from queue
        sends "start" notification on first run whe some data arrives from stdin
        """
        if not self.stdin_line_queue.empty():
            if not self.read_started:
                self.callback("start")
                self.read_started = True

            if(not self.paused):
                self.callback(self.stdin_line_queue.get())

    def set_interval(self, interval_ms):
        self.timeout = interval_ms
        self.timer.setInterval(interval_ms)

    def set_paused(self, paused=True):
        self.paused = paused
