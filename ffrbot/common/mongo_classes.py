from typing import *


class GuildConfig(TypedDict):
    id: int
    admin_role_ids: Optional[List[int]]
    polls_category_id: Optional[int]
    role_requests_channel_id: Optional[int]
    race_org_channel_id: Optional[int]
    race_results_channel_id: Optional[int]


class SelfAssignableRoleConfig(TypedDict):
    id: int
    msg_to_role_map: Dict[int, int]


class User(TypedDict):
    id: int
    twitch_id: str


class Race(TypedDict):
    race_type: Literal["sync", "async"]
    guild_id: int


class RoleConfig(TypedDict):
    guild_id: int
