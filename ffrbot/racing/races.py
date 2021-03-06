import pickle
from typing import *

import redis

from discord.ext import commands

# from ..common import checks
from ..common import config
import logging

# from ..common import constants
from .sync_race import SyncRace
from .async_race import AsyncRace
from ..common.redis_client import RedisClient, Namespace, RaceKeys
from .race import Race

allow_races_bool: bool = True


def is_race_channel(ctx):
    return ctx.channel.name == config.get_race_org_channel_id()


def allow_races(ctx):
    return allow_races_bool


class Races(commands.Cog):
    def __init__(self, bot, db):
        self.bot: commands.Bot = bot
        self.db: RedisClient = db
        self.sync_races: TypedDict[str, SyncRace] = dict()
        self.async_races: TypedDict[str, AsyncRace] = dict()
        self.twitch_ids: TypedDict[str, str] = dict()

    def load_data(self) -> None:
        temp_sync_races = self.db.get_obj_dict(
            Namespace.RACE_CONFIG, RaceKeys.SYNC_RACES
        )

        temp_async_races = self.db.get_obj_dict(
            Namespace.RACE_CONFIG, RaceKeys.ASYNC_RACES
        )

        temp_twitch_ids = dict(self.db.hgetall("twitchids"))
        for k, v in temp_twitch_ids.items():
            self.twitch_ids[k.decode("utf-8")] = v.decode("utf-8")

    def save_race(self, race: Race) -> None:
        race_type = "sync_race" if isinstance(race, SyncRace) else "async_race"

        self.db.hset(
            race_type,
            race.id,
            pickle.dumps(race, protocol=pickle.HIGHEST_PROTOCOL),
        )

    def verify_save(self, race: Race) -> None:
        race_type = "sync_race" if isinstance(race, SyncRace) else "async_race"
        saved_version = pickle.loads(self.db.hget(race_type, race.id))
        logging.debug("original: " + str(race))
        logging.debug("saved: " + str(saved_version))
        logging.debug(saved_version == race)

    @commands.command(aliases=["sr", "startrace"])
    @commands.check(is_race_channel)
    @commands.check(allow_races)
    async def start_race(self, ctx, *, name=None):
        if name is None:
            await ctx.author.send("you forgot to name your race")
            return
