from ..common.discord_user import DiscordUser


class Racer(DiscordUser):
    """
    a class for a discord user racing
    """
    def __init__(self, user_id: str, name: str, display_name: str):
        super().__init__(user_id, name, display_name)

