from discord.ext.commands import Bot
import discord
from typing import *
from pymongo import MongoClient
import logging

from .guild_config import *
from .role_config import *


__db: MongoClient
__bot: Bot


def init(db: MongoClient, bot: Bot) -> None:
    logging.warn("\n\n\nasdf\n\n\n")
    global __db
    global __bot
    __db = db
    __bot = bot

    init_guild_config(db, bot)
    init_role_config(db, bot)
