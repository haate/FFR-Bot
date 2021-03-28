from abc import ABC, abstractmethod
from typing import *
from ...common.discord_user import DiscordUser


class Race(ABC):
    """
    An abstract class to model a race
    """

    def __init__(self) -> None:
        self._runners: Dict[int, DiscordUser] = dict()
        self._name: str = ""
        self._finished: bool = False
        self._id: int = -1

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def finished(self) -> bool:
        return self._finished

    @finished.setter
    def finished(self, value: bool) -> None:
        self._finished = value

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        self._id = value

    @property
    def runners(self) -> Dict[int, DiscordUser]:
        return self._runners

    @abstractmethod
    def remove_runner(self, runner: DiscordUser) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_race(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def forfeit_runner(self, runner: DiscordUser) -> None:
        raise NotImplementedError

    @abstractmethod
    def end_race(self) -> None:
        raise NotImplementedError


class RaceNotStarted(Exception):
    """
    raised when the race has not started yet but was expected to have.
    """

    pass


class RaceAlreadyStarted(Exception):
    """
    raised when the race has already started and the action is not allowed.
    """

    pass
