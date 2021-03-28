import sys
import time
import asyncio
import logging
from watchdog.observers import Observer  # type: ignore
from watchdog.events import LoggingEventHandler  # type: ignore
import multiprocessing
from typing import *

from . import bot


class Event(LoggingEventHandler):  # type: ignore
    def __init__(self, process: Optional[multiprocessing.Process]):
        super().__init__()
        self.bot_process = process

    def event_loop_wrapper(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot.main()

    def dispatch(self, event: Any) -> None:
        logging.info(event)
        if self.bot_process is not None:
            self.bot_process.terminate()
        self.bot_process = multiprocessing.Process(
            target=self.event_loop_wrapper, daemon=True
        )
        self.bot_process.start()


def handle_exit(observer: Any) -> None:
    try:
        observer.stop()
    except Exception:
        pass


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    bot_process: multiprocessing.Process = multiprocessing.Process(
        target=bot.main, daemon=True
    )
    bot_process.start()
    path = sys.argv[1] if len(sys.argv) > 1 else "./ffrbot"
    event_handler = Event(bot_process)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            handle_exit(observer)
            break
        except Exception as e:
            logging.exception(e)
            handle_exit(observer)
