from discord.ext import commands
import re
from math import ceil
from random import random
from typing import List


class RNG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def roll(self, ctx, dice):
        match = re.match(r"((\d{1,3})?d\d{1,9})", dice)
        if match is None:
            await ctx.message.channel.send(
                "Roll arguments must be in the form [N]dM ie. 3d6, d8"
            )
            return
        roll_args: List[int] = [int(num) for num in match.group().split("d")]

        try:
            roll_args[0] = int(roll_args[0])
        except ValueError:
            roll_args[0] = 1
        roll_args[1] = int(roll_args[1])
        result = [ceil(random() * roll_args[1]) for _ in range(roll_args[0])]
        text_result = "{} result: **{}**".format(match.group(), sum(result))
        await ctx.message.channel.send(text_result)

    @commands.command()
    async def coin(self, ctx):
        coin_res: str
        if random() >= 0.5:
            coin_res = "Heads"
        else:
            coin_res = "Tails"
        await ctx.message.channel.send(
            "Coin landed on: **{}**".format(coin_res)
        )
