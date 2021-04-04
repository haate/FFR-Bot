import pickle
from typing import *
from pymongo import MongoClient

from discord.ext import commands
import discord

from ...common import config
import logging

from .sync_race import SyncRace
from .async_race import AsyncRace
from .race import Race


def is_race_channel(ctx: commands.Context) -> bool:
    if isinstance(ctx.channel, discord.TextChannel) and isinstance(
        ctx.guild, discord.Guild
    ):
        return ctx.channel.id == config.get_race_org_channel_id(ctx.guild.id)
    else:
        return False


class Races(commands.Cog):
    def __init__(self, bot: commands.Bot, db: MongoClient) -> None:
        self.bot = bot
        self.db = db
        self.sync_races: Dict[str, SyncRace] = dict()
        self.async_races: Dict[str, AsyncRace] = dict()
        self.twitch_ids: Dict[str, str] = dict()

    def get_active_sync_race_ids(self) -> List[int]:
        sync_races_collection = self.db.races.sync_races
        sync_race_ids = list(
            sync_races_collection.find({"active": {"$eq": True}}, ["id"])
        )
        logging.info("active sync race ids")
        logging.info(str(sync_race_ids))
        return sync_race_ids

    def get_active_async_race_ids(self) -> List[int]:
        async_races_collection = self.db.races.async_races
        async_race_ids = list(
            async_races_collection.find({"active": {"$eq": True}}, ["id"])
        )
        logging.info("active async race ids")
        logging.info(str(async_race_ids))
        return async_race_ids

    def get_all_sync_race_ids(self) -> List[int]:
        sync_races_collection = self.db.races.sync_races
        sync_race_ids = list(
            sync_races_collection.find({}, ["id"])
        )
        logging.info("all sync race ids")
        logging.info(str(sync_race_ids))
        return sync_race_ids

    def get_all_async_race_ids(self) -> List[int]:
        async_races_collection = self.db.races.async_races
        async_race_ids = list(
            async_races_collection.find({}, ["id"])
        )
        logging.info("all async race ids")
        logging.info(str(async_race_ids))
        return async_race_ids
    
    


    @commands.command(aliases=["sr", "startrace"])
    # @commands.check(is_race_channel)
    @commands.guild_only()
    async def start_race(self, ctx: commands.Context, *name_list: str) -> None:
        assert isinstance(ctx.guild, discord.Guild)
        if len(name_list) == 0:
            await ctx.author.send("you forgot to name your race")
            raise Exception("no name for race in start race command")
        
        name = " ".join(name_list)
        guild_id = ctx.guild.id

        
        
