from . import text


async def wait_for_yes_no(
    bot, ctx, question_text, yes_cb, no_cb=None, timeout=120
):
    await ctx.channel.send(question_text)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    reply = None
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
