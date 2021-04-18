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


def init_guild(guild: discord.Guild) -> None:
    __db.guilds.configs.insert_one({"id": guild.id})


def get_guild_config(guild_id: int) -> Optional[GuildConfig]:
    return __db.guilds.configs.find_one({"id": guild_id})


def get_admin_role_ids(guild_id: int) -> Optional[List[int]]:
    config = get_guild_config(guild_id)
    if config is None:
        return None
    try:
        return config["admin_role_ids"]
    except KeyError:
        return None


def add_admin_role_ids(guild_id: int, new_admins: List[int]) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id},
        {"$addToSet": {"admin_role_ids": {"$each": new_admins}}},
    )


def remove_admin_role_ids(guild_id: int, stale_admins: List[int]) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id},
        {"$pullAll": {"admin_role_ids": stale_admins}},
    )


def get_polls_category_id(guild_id: int) -> Optional[int]:
    config = get_guild_config(guild_id)
    if config is None:
        return None
    try:
        return config["polls_category_id"]
    except KeyError:
        return None


def set_polls_category_id(guild_id: int, value: int) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id}, {"$set": {"polls_category_id": value}}
    )


def get_role_requests_channel_id(guild_id: int) -> Optional[int]:
    config = get_guild_config(guild_id)
    if config is None:
        return None
    try:
        return config["role_requests_channel_id"]
    except KeyError:
        return None


def set_role_requests_channel_id(guild_id: int, value: int) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id}, {"$set": {"role_requests_channel_id": value}}
    )


def get_race_org_channel_id(guild_id: int) -> Optional[int]:
    config = get_guild_config(guild_id)
    if config is None:
        return None
    try:
        return config["race_org_channel_id"]
    except KeyError:
        return None


def set_race_org_channel_id(guild_id: int, value: int) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id}, {"$set": {"race_org_channel_id": value}}
    )


def get_race_results_channel_id(guild_id: int) -> Optional[int]:
    config = get_guild_config(guild_id)
    if config is None:
        return None
    try:
        return config["race_results_channel_id"]
    except KeyError:
        return None


def set_race_results_channel_id(guild_id: int, value: int) -> None:
    __db.guilds.configs.update_one(
        {"id": guild_id}, {"$set": {"race_results_channel_id": value}}
    )