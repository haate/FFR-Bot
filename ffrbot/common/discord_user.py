from typing import *
from pymongo import MongoClient
from discord.ext import commands


class DiscordUser:
    def __init__(self, user_id: int, bot: commands.Bot, db: MongoClient):
        self.user_id = user_id
        self.__bot = bot
        self.__db = db
        self.__twitch_id: Optional[str] = None

    def display_name(self, guild_id: int) -> str:
        return (
            self.__bot.get_guild(guild_id)
            .get_member(self.user_id)
            .display_name
        )

    @property
    def name(self) -> str:
        user = self.__bot.get_user(self.user_id)
        return user.name if user is not None else "User name not found"

    def delete(self) -> None:
        """
        This deletes all bot saved data about this user
        """
        del self.twitch_id

    @property
    def twitch_id(self) -> Optional[str]:
        twitch_info = self.__db.users.twitch.find_one(
            {"user_id": self.user_id}
        )
        if twitch_info is not None:

            try:
                twitch_id: str = twitch_info["twitch_id"]
                return twitch_id
            except KeyError:
                return None
        else:
            return None

    @twitch_id.setter
    def twitch_id(self, value: str) -> None:
        self.__db.users.twitch.update_one(
            {"user_id": self.user_id}, {"$set": {"twitch_id": value}}
        )

    @twitch_id.deleter
    def twitch_id(self) -> None:
        self.__db.users.twitch.update_one(
            {"user_is": self.user_id}, {"$unset": {"twitch_id": ""}}
        )
