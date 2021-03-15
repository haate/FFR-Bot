from .redis_client import RedisClient, Namespace, UserKeys
from typing import *
from .config import get_guild
import discord


class DiscordUser:
    def __init__(self, user_id: int, db: RedisClient):
        self.user_id = user_id
        self.__db: RedisClient = db
        self.__twitch_id: Optional[str] = None

    @property
    def display_name(self) -> str:
        member: Optional[discord.Member] = get_guild().get_member(self.user_id)
        return member.display_name if member else ""

    @property
    def name(self) -> str:
        member: Optional[discord.Member] = get_guild().get_member(self.user_id)
        return member.name if member else ""

    @property
    def twitch_id(self) -> str:
        return self.__twitch_id

    @twitch_id.setter
    def twitch_id(self, value: str) -> None:
        self.__twitch_id = value

    @twitch_id.deleter
    def twitch_id(self) -> None:
        del self.__twitch_id
