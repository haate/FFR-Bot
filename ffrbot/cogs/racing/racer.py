from ffrbot.common.discord_user import DiscordUser
from ffrbot.common.redis_client import RedisClient


class Racer(DiscordUser):
    """
    TODO: needed?

    a class for a discord user racing
    """

    def __init__(self, user_id: int, db: RedisClient):
        super().__init__(user_id, db)
