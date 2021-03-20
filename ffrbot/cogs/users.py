from discord.ext import commands
from typing import *
import discord
import re
import logging
from ..common import text

from ..common.redis_client import RedisClient, Namespace, UserKeys
from ..common.discord_user import DiscordUser
from ..common.snippits import wait_for_yes_no


class Users(commands.Cog):
    """
    Users related commands
    """

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

    @commands.command(aliases=["twitchid", "settwitchid"])
    async def set_twitch_id(self, ctx: commands.Context, value: str) -> None:
        """
        Sets your twitch id to the linked id, can pull the id from a url
        """
        user = self.get_user(ctx.author.id)

        if "twitch.tv" in value:
            # We need to parse the url for their twitch id
            try:
                match = re.search(r"twitch\.tv/[^/?]*", value)
                twitch_id = (
                    match[0].split("/")[1] if match is not None else None
                )
            except Exception:
                await ctx.channel.send(text.set_twitch_id_not_found)
                raise Exception("twitch id not found, exiting early")
        else:
            twitch_id = value

        if twitch_id is None or twitch_id == "":
            await ctx.channel.send(text.set_twitch_id_not_found)
            raise Exception("twitch id not found, exiting early")

        async def yes():
            user.twitch_id = id

        await wait_for_yes_no(
            self.bot,
            ctx,
            f"Your twitch id will be set to: {twitch_id}\n Type yes to confirm"
            f" or no to abort.",
            yes,
        )

        user.twitch_id = value

    @commands.command(aliases=["gettwitch", "gettwitchlink"])
    async def get_twitch_link(self, ctx: commands.Context) -> None:
        """
        Gets your twitch link or the twitch link for any mentioned members
        """

        msg: discord.Message = ctx.message
        mentions = msg.mentions
        if not mentions:
            if self.get_user(ctx.author.id).twitch_id is not None:
                await ctx.channel.send(
                    "https://twitch.tv/"
                    + self.get_user(ctx.author.id).twitch_id
                )
            else:
                await ctx.channel.send(text.get_twitch_id_not_found)

        else:
            send_msg = ""
            no_twitch_id: List[DiscordUser] = []
            for mention in mentions:
                user = self.get_user(mention.id)
                if user.twitch_id is None:
                    no_twitch_id.append(user)
                else:
                    send_msg += f"<https://twitch.tv/{user.twitch_id}>\n"

            send_msg += text.list_people_no_twitch_id_set(
                [x.name for x in no_twitch_id]
            )
            await ctx.channel.send(send_msg)

    @commands.command(aliases=["deletemydata", "deleteme"])
    async def delete_saved_data(self, ctx: commands.Context) -> None:
        """
        Removes all saved info about you, discord provided data will still be
        available to the bot.
        """

        async def yes():
            user = self.get_user(ctx.author.id)
            user.delete()

        await wait_for_yes_no(self.bot, ctx, text.delete_user_data_yes_no, yes)
