from discord.ext import commands
from typing import *
import discord
import re
import logging

from ..common.redis_client import RedisClient, Namespace, UserKeys
from ..common.discord_user import DiscordUser
from ..common.snippits import wait_for_yes_no


class Users(commands.Cog):
    def __init__(self, bot: commands.Bot, db: RedisClient):
        logging.info("initializing Users Cog")
        self.db = db
        self.bot = bot
        self.users: Dict[int, DiscordUser] = dict()

    def get_user(self, user_id: int) -> DiscordUser:
        try:
            user = self.users[user_id]
        except KeyError:
            user = DiscordUser(user_id, self.db)
            self.users[user_id] = user
        return user

    @commands.command()
    async def set_twitch_id(self, ctx: commands.Context, value: str) -> None:
        user = self.get_user(ctx.author.id)

        if "twitch.tv" in value:
            # We need to parse the url for their twitch id
            match = re.match(r"twitch\.tv\/([^/?]*)", value)
            logging.info(match)
            value = match[0]

        async def yes():
            user.twitch_id = value

        await wait_for_yes_no(
            self.bot,
            ctx,
            f"Your twitch id will be set to: {value}\n Type yes to confirm or"
            f" no to abort.",
            yes,
        )

        user.twitch_id = value
