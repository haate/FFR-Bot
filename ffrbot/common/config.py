from .redis_client import *
from discord.ext.commands import Bot
from discord import Guild
from typing import *

__db: RedisClient
__bot: Bot
__cache: Dict[Union[str, int], Any] = dict()


def init(db: RedisClient, bot: Bot) -> None:
    global __db
    global __bot
    __db = db
    __bot = bot


def get_admin_role_ids() -> Set[int]:
    return (
        __db.get_int_set(Namespace.ADMIN_CONFIG, AdminKeys.ROLE_IDS) or set()
    )


def set_admin_role_ids(new_admins: Iterable[int]) -> None:
    current_admins = get_admin_role_ids()

    __db.set_int_set(
        Namespace.ADMIN_CONFIG,
        AdminKeys.ROLE_IDS,
        current_admins.union(set([int(admin_id) for admin_id in new_admins])),
    )


def get_polls_category_id() -> int:
    return int(
        __db.get_str(Namespace.ADMIN_CONFIG, AdminKeys.POLLS_CATEGORY) or "-1"
    )


def set_polls_category_id(value: int) -> None:
    __db.set_str(Namespace.ADMIN_CONFIG, AdminKeys.POLLS_CATEGORY, str(value))


def get_role_requests_channel_id() -> int:
    r_val = int(
        __db.get_str(Namespace.ADMIN_CONFIG, AdminKeys.ROLE_REQUESTS_CHANNEL)
        or "-1"
    )
    return r_val


def set_role_requests_channel_id(value: int) -> None:
    __db.set_str(
        Namespace.ADMIN_CONFIG, AdminKeys.ROLE_REQUESTS_CHANNEL, str(value)
    )


def get_race_org_channel_id() -> int:
    return int(
        __db.get_str(Namespace.RACE_CONFIG, RaceKeys.ORG_CHANNEL_ID) or "-1"
    )


def set_race_org_channel_id(value: int) -> None:
    __db.set_str(Namespace.RACE_CONFIG, RaceKeys.ORG_CHANNEL_ID, str(value))


def get_race_results_channel_id() -> int:
    return int(
        __db.get_str(Namespace.RACE_CONFIG, RaceKeys.RESULTS_CHANNEL_ID) or ""
    )


def set_race_results_channel_id(value: int) -> None:
    __db.set_str(
        Namespace.RACE_CONFIG, RaceKeys.RESULTS_CHANNEL_ID, str(value)
    )


def set_guild_id(value: int) -> None:
    __db.set_str(Namespace.ADMIN_CONFIG, AdminKeys.GUILD_ID, str(value))


def get_guild_id() -> int:
    return int(
        __db.get_str(Namespace.ADMIN_CONFIG, AdminKeys.GUILD_ID) or "-1"
    )


def get_guild() -> Guild:
    guild_id = get_guild_id()
    if guild_id in __cache.keys():
        return cast(Guild, __cache[guild_id])
    else:
        # we cast here since we assert that the bot is in a guild
        guild = cast(Guild, __bot.get_guild(int(get_guild_id())))
        assert guild is not None
        __cache[guild_id] = guild
        return guild
