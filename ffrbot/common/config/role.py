from discord.ext.commands import Bot
import discord
from typing import *
from pymongo import MongoClient
import logging

from ..mongo_classes import *

__db: MongoClient
__bot: Bot


def init(db: MongoClient, bot: Bot) -> None:
    global __db
    global __bot
    __db = db
    __bot = bot


def get_role_config(guild_id: int) -> Optional[RoleConfig]:
    return __db.guilds.role_configs.find_one({"guild_id": guild_id})


def get_self_assignable_roles(
    guild_id: int,
) -> Optional[Set[SelfAssignableRole]]:
    role_config = get_role_config(guild_id)
    if role_config:
        return role_config["self_assignable_roles"]
    else:
        return None


def add_self_assignable_roles(
    guild_id: int, roles: Set[SelfAssignableRole]
) -> None:

    pass


def remove_self_assignable_roles(guild_id: int, role_ids: Set[int]) -> None:

    pass