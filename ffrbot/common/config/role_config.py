from discord.ext.commands import Bot
import discord
from typing import *
from pymongo import MongoClient
import logging

from ..mongo_classes import *

__db: MongoClient
__bot: Bot


def init_role_config(db: MongoClient, bot: Bot) -> None:
    global __db
    global __bot
    __db = db
    __bot = bot


def getRoleConfig(guild_id: int) -> Optional[RoleConfig]:
    return __db.guilds.role_configs.find_one({"guild_id": guild_id})
