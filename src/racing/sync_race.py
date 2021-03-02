from typing import *

from .race import Race
from .racer import Racer

import asyncio
import time
import random

import urllib
import urllib.request
import json
from io import StringIO

from discord.ext import commands
from discord.utils import get

import logging

from .. import constants


class SyncRacer(Racer):
    """
    A class to model a racer in a synchronous race
    """

    def __init__(self, user_id: str, name: str, display_name: str) -> None:
        super().__init__(user_id, name, display_name)

        self.readied = False
        self.time: Optional[int] = None
        self.forfeited = False

    def set_forfeited(self, is_forfeited: bool) -> None:
        self.forfeited = is_forfeited

    def get_forfeited(self) -> bool:
        return self.forfeited

    def set_readied(self, is_readied: bool) -> None:
        self.readied = is_readied

    def get_readied(self) -> bool:
        return self.readied

    def get_finished(self) -> bool:
        return self.time is not None or self.forfeited


class SyncRace(Race):
    """
    A class to model a synchronous race
    """

    def __init__(self, name: str, id: str) -> None:
        self.runners: TypedDict[str, SyncRacer] = dict()
        self.start_time: Optional[int] = None
        self.name: str = name
        self.id: str = id
        self.finished: bool = False

    def get_started(self) -> bool:
        return self.start_time is not None

    def add_runner(self, runner: SyncRacer) -> None:
        self.runners[runner.user_id] = runner

    def remove_runner(self, runner: SyncRacer) -> None:
        if not self.get_started():
            del self.runners[runner.user_id]

    def start_race(self) -> None:
        if not self.get_started():
            self.start_time = time.time_ns()

    def forfeit_runner(self, runner: SyncRacer) -> None:
        self.runners[runner.user_id].set_forfeited(True)

    def end_race(self):
        self.finished = True
        [runner.set_forfeited(True) for runner in self.runners.values() if
         runner.get_finished()]

    def check_readied(self):
        return len([runner for runner in self.runners.values() if
                    runner.readied is False]) == 0
