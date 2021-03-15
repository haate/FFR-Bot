from typing import *

from .sync_race import SyncRacer, SyncRace


class TeamSyncRacer(SyncRacer):
    def __init__(self, user_id: str, name: str, display_name: str):
        super().__init__(user_id, name, display_name)
        self.team_name: Optional[str] = None
        self.team_id: Optional[str] = None


class Team(TypedDict):
    name: str
    id: str
    members: Dict[str, TeamSyncRacer]


class TeamSyncRace(SyncRace):
    def __init__(self, name: str):
        super().__init__(name)
        self.teams: Dict[str, Team] = dict()

    def add_team(self, team_name: str, team_id: str) -> None:
        self.teams[team_id] = Team(name=team_name, id=team_id, members=dict())

    def add_team_member(self, team_id, runner: TeamSyncRacer) -> None:
        team = self.teams[team_id]
        if team is not None:
            runner.team_id = team_id
            runner.team_name = team["name"]
            team["members"][runner.user_id] = runner

    def remove_team_member(self, team_id: str, runner: TeamSyncRacer) -> None:
        team = self.teams[team_id]
        if team is not None:
            runner.team_id = None
            runner.team_name = None
            del team["members"][runner.user_id]

    def remove_runner(self, runner: TeamSyncRacer) -> None:
        if runner.team_id is not None:
            self.remove_team_member(runner.team_id, runner)
        super().remove_runner(runner)

    def remove_team(self, team_id: str):
        del self.teams[team_id]
