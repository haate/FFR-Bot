from abc import ABC, abstractmethod
from typing import Dict
from .racer import Racer


class Race(ABC):
    """
    An abstract class to model a race
    """

    def __init__(self):
        self._runners = dict()
        self._name: str = ""
        self._finished: bool = False
        self._id: str = ""

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def finished(self) -> bool:
        return self._finished

    @finished.setter
    def finished(self, value: bool):
        self._finished = value

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def runners(self) -> Dict[str, Racer]:
        return self._runners

    @abstractmethod
    def remove_runner(self, runner: Racer):
        raise NotImplementedError

    @abstractmethod
    def start_race(self):
        raise NotImplementedError

    @abstractmethod
    def forfeit_runner(self, runner: Racer):
        raise NotImplementedError

    @abstractmethod
    def end_race(self):
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
