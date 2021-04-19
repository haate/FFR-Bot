import sys
import time
import asyncio
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import multiprocessing
from typing import *
import importlib
from threading import Timer


# These are the sequences need to get colored ouput
grey = "\x1b[38;21m"
yellow = "\x1b[33;21m"
red = "\x1b[31;21m"
green = "\x1b[32;21m"
bold_red = "\x1b[31;1m"
reset = "\x1b[0m"


class Event(FileSystemEventHandler):  # type: ignore
    def __init__(
        self,
        process: Optional[multiprocessing.Process] = None,
    ):

        super().__init__()
        self.bot_process = process
        self.timeout: Optional[Timer] = None

    def event_loop_wrapper(self) -> None:
        try:
            if "ffrbot.bot" not in sys.modules:
                importlib.import_module("ffrbot.bot")
            else:
                importlib.reload(bot)
        except Exception as e:
            logging.exception(e)
            return
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        bot.main()

    def re_import(self) -> None:
        logging.info(
            green + "re-importing and running with saved changes" + reset
        )
        if self.bot_process is not None:
            try:
                self.bot_process.terminate()
                self.bot_process.close()
            except Exception as e:
                del self.bot_process
                pass
        try:
            self.bot_process = multiprocessing.Process(
                target=self.event_loop_wrapper, daemon=True
            )
            self.bot_process.run()
        except Exception as e:
            logging.exception(e)
            pass

    def on_any_event(self, event: Any) -> None:
        if "__pycache__" in event.src_path:
            return
        logging.debug(event)
        logging.debug(self.timeout)
        if self.timeout:
            self.timeout.cancel()
            del self.timeout

        self.timeout = Timer(0.5, self.re_import)
        self.timeout.start()


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

    try:
        from . import bot
    except Exception as e:
        logging.exception(e)
        pass

    bot_process: Optional[multiprocessing.Process] = None
    try:
        bot_process = multiprocessing.Process(target=bot.main, daemon=True)
        bot_process.start()
    except Exception as e:
        logging.exception(e)
        pass
    path = sys.argv[1] if len(sys.argv) > 1 else "./ffrbot"
    if bot_process is not None:
        event_handler = Event(bot_process)
    else:
        event_handler = Event()
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
