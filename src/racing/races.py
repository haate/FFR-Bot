import asyncio
import pickle
from typing import *
import random

import urllib
import urllib.request
import json
from io import StringIO
import redis

from discord.ext import commands
from discord.utils import get

from .race import Race
import logging

from .. import constants
from .sync_race import SyncRace
from .async_race import AsyncRace
from .race import Race

allow_races_bool: bool = True

def is_race_channel(ctx):
    return ctx.channel.name == constants.call_for_races_channel

def allow_races(ctx):
    return allow_races_bool

def is_admin(ctx):
    user = ctx.author
    return (any(role.name in constants.ADMINS for role in user.roles)) or (
            user.id == int(140605120579764226))

def is_bot_admin(ctx: commands.Context):
    user = ctx.author
    return user.id == constants.bot_admin_id


class Races(commands.Cog):
    def __init__(self, bot, db):
        self.bot: commands.Bot = bot
        self.db: redis.StrictRedis = db
        self.sync_races: TypedDict[str, SyncRace] = dict()
        self.async_races: TypedDict[str, AsyncRace] = dict()
        self.twitch_ids: TypedDict[str, str] = dict()

    def load_data(self) -> None:
        temp_sync_races = dict(self.db.hget('sync_races'))
        for k, v in temp_sync_races.items():
            self.sync_races[k.decode('utf-8')] = pickle.loads(v)

        temp_async_races = dict(self.db.hget('async_races'))
        for k, v in temp_async_races.items():
            self.async_races[k.decode('utf-8')] = pickle.loads(v)

        temp_twitch_ids = dict(self.db.hgetall('twitchids'))
        for k, v in temp_twitch_ids.items():
            self.twitch_ids[k.decode('utf-8')] = v.decode('utf-8')

    def save_race(self, race: Race) -> None:
        race_type = 'sync_race' if isinstance(race, SyncRace) else 'async_race'

        self.db.hset(race_type, race.id,
                     pickle.dumps(race, protocol=pickle.HIGHEST_PROTOCOL))

    def verify_save(self, race: Race) -> None:
        race_type = 'sync_race' if isinstance(race, SyncRace) else 'async_race'
        saved_version = pickle.loads(self.db.hget(race_type, race.id))
        logging.debug("original: " + str(race))
        logging.debug("saved: " + str(saved_version))
        logging.debug(saved_version == race)


    @commands.command()
    @commands.check(is_bot_admin)



    @commands.command(aliases=['sr'])
    @commands.check(is_race_channel)
    @commands.check(allow_races)
    async def startrace(self, ctx, *, name=None):
        if name is None:
            await ctx.author.send("you forgot to name your race")
            return


