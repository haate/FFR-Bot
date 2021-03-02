from abc import ABC, abstractmethod
from typing  import TypedDict
from .racer import Racer


class Race(ABC):
    """
    An abstract class to model a race
    """
    id: str
    name: str
    finished: bool
    runners: TypedDict[str, Racer]

    @abstractmethod
    def add_runner(self, runner: Racer):
        pass

    @abstractmethod
    def remove_runner(self, runner: Racer):
        pass

    @abstractmethod
    def start_race(self):
        pass

    @abstractmethod
    def forfeit_runner(self, runner: Racer):
        pass

    @abstractmethod
    def end_race(self):
        pass


class RaceNotStarted(Exception):
    """
    raised when the race has not started yet but was expected to have.
    """
    pass
