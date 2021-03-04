import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import multiprocessing
from typing import Optional

from . import bot


class Event(LoggingEventHandler):
    def __init__(self, process: Optional[multiprocessing.Process]):
        super().__init__()
        self.bot_process = process

    def dispatch(self, event):
        logging.info(event)
        if self.bot_process is not None:
            self.bot_process.terminate()
        self.bot_process = multiprocessing.Process(
            target=bot.main, daemon=True
        )
        self.bot_process.start()


if __name__ == "__main__":
    bot_process: Optional[multiprocessing.Process] = multiprocessing.Process(
        target=bot.main, daemon=True
    )
    bot_process.start()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    path = sys.argv[1] if len(sys.argv) > 1 else "./ffrbot"
    event_handler = Event(bot_process)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
