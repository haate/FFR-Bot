from typing import *

from .race import Race
from ...common.discord_user import DiscordUser
from ...common.redis_client import RedisClient


class AsyncRacer(DiscordUser):
    """
    A class to model a racer in a synchronous race
    """

    def __init__(self, user_id: int, db: RedisClient) -> None:
        super().__init__(user_id, db)

        self.time: Optional[int] = None
        self.forfeited = False

    def set_forfeited(self, is_forfeited: bool) -> None:
        self.forfeited = is_forfeited

    def get_forfeited(self) -> bool:
        return self.forfeited

    def get_finished(self) -> bool:
        return self.time is not None or self.forfeited


class AsyncRace(Race):
    """
    A class to model an asynchronous race
    """

    def __init__(self, name: str, id: str) -> None:
        self.runners: TypedDict[str, AsyncRacer] = dict()
        self.started: bool = False
        self.name: str = name
        self.id: str = id
        self.finished: bool = False

    def get_started(self) -> bool:
        return self.started

    def add_runner(self, runner: AsyncRacer) -> None:
        self.runners[runner.user_id] = runner

    def remove_runner(self, runner: AsyncRacer) -> None:
        if not self.get_started():
            del self.runners[runner.user_id]

    def start_race(self) -> None:
        self.started = True

    def forfeit_runner(self, runner: AsyncRacer) -> None:
        self.runners[runner.user_id].set_forfeited(True)

    def end_race(self):
        self.finished = True
        [
            runner.set_forfeited(True)
            for runner in self.runners.values()
            if runner.get_finished()
        ]
