from . import text
from discord.ext.commands import Bot, Context
from discord import Message
from typing import *


async def wait_for_yes_no(
    bot: Bot,
    ctx: Context,
    question_text: str,
    yes_cb: Callable[[], Awaitable[None]],
    no_cb: Optional[Callable[[], Awaitable[None]]] = None,
    timeout: int = 120,
) -> None:
    await ctx.channel.send(question_text)

    def check(m: Message) -> bool:
        return m.author == ctx.author and m.channel == ctx.channel

    reply: Optional[Message] = None
    while reply is None or not (
        reply.content.lower() == "yes" or reply.content.lower() == "no"
    ):
        try:
            reply = await bot.wait_for("message", timeout=timeout, check=check)
        except TimeoutError:
            await ctx.author.send(text.timeout)
            return
    if reply.content.lower() == "yes":
        await yes_cb()
    else:
        if no_cb:
            await no_cb()
