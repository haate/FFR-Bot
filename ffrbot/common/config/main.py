from discord.ext.commands import Bot
import discord
from typing import *
from pymongo import MongoClient
import logging

from . import guild, role


__db: MongoClient
__bot: Bot


def init(db: MongoClient, bot: Bot) -> None:
    global __db
    global __bot
    __db = db
    __bot = bot

    guild.init(db, bot)
    role.init(db, bot)
