import logging
import time

from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.txt"]

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def process(self, event):
        logging.info("file under watching: {0} has event: {1}".format(event.src_path, event.event_type))
        self.callback()

    def on_modified(self, event):
        self.process(event)


def watch_modify(path, callback):
    observer = Observer()
    observer.schedule(MyHandler(callback), path=path)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
