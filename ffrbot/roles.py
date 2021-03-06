from discord.ext import commands

import discord
from .common.snippits import wait_for_yes_no
import logging
from typing import *
from .common import config, checks, text
from .common.redis_client import RedisClient, Namespace, RoleKeys
from discord.utils import get

from .common import constants


def is_role_requests_channel(ctx):
    return str(ctx.channel.id) == config.get_role_requests_channel_id()


class Roles(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db: RedisClient = db

    @commands.command()
    @commands.check(is_role_requests_channel)
    async def addrole(self, ctx, *, role=None):
        if role is None:
            await ctx.author.send("you forget to ask for a role")
            await ctx.message.delete()
            return
        role_clean = role.lower().strip("\"'")
        if role_clean not in [
            x.lower() for x in constants.self_assignable_roles
        ]:
            await ctx.author.send(
                "you cannot give yourself the role: "
                + role
                + "\n or that role doesnt exist"
            )
            await ctx.message.delete()
        else:
            roles = ctx.message.guild.roles
            role_obj = get(
                roles,
                name=next(
                    x
                    for x in constants.self_assignable_roles
                    if x.lower() == role_clean
                ),
            )
            await ctx.author.add_roles(role_obj)

    @commands.command()
    @commands.check(is_role_requests_channel)
    async def removerole(self, ctx, *, role=None):
        if role is None:
            await ctx.author.send("you forget to say which role to remove")
            await ctx.message.delete()
            return
        role_clean = role.lower().strip("\"'")
        if role_clean not in [
            x.lower() for x in constants.self_assignable_roles
        ]:
            await ctx.author.send(
                "you cannot remove yourself from the role: "
                + role
                + "\n or that role doesnt exist"
            )
            await ctx.message.delete()
        else:
            roles = ctx.message.guild.roles
            role_obj = get(
                roles,
                name=next(
                    x
                    for x in constants.self_assignable_roles
                    if x.lower() == role_clean
                ),
            )
            await ctx.author.remove_roles(role_obj)

    @commands.command()
    @checks.is_admin()
    async def add_self_assignable_role(self, ctx: commands.Context, *args):

        msg: discord.Message = ctx.message
        guild: discord.Guild = ctx.guild
        descriptions: List[str] = []
        roles: List[discord.Role] = []

        for i in range(len(args) // 2):
            role_name = args[i]
            role = [role for role in guild.roles if role.name == role_name][0]
            if role is None:
                await ctx.author.send(
                    'could not find the role named: "' + role_name + '"'
                )
                ctx.message.delete()
                raise Exception("couldn't find role name: " + role_name)
            roles.append(role)
            descriptions.append(args[i + 1])

            async def add_roles():
                self.db.set_set(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.SELF_ASSIGNABLE_ROLE_IDS,
                    [x.id for x in roles],
                )
                self.db.set_str_dict(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES,
                    dict([(x.id, x.name) for x in roles]),
                )
                self.db.set_str_dict(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.SELF_ASSIGNABLE_ROLE_DESCRIPTIONS,
                    dict([(descriptions,
                )
                await ctx.channel.send(text.roles_added)

            async def no_change():
                await ctx.channel.send(text.roles_not_added)

            question = text.roles_look_ok + "\n"

            for j in range(len(roles)):
                role = roles[j]
                description = descriptions[j]
                question += (
                    "\nname: " + role.name + ", description: " + description
                )

            await wait_for_yes_no(
                self.bot, ctx, question, add_roles, no_change
            )

    @commands.command()
    @commands.check(is_role_requests_channel)
    async def list_roles(self, ctx):
        role_ids: Set[str] = self.db.get_set(
            Namespace.ROLE_CONFIG, RoleKeys.SELF_ASSIGNABLE_ROLE_IDS
        )
        logging.warning("role stuff: " + str(role_ids))

        descriptions: Dict[str, str] = self.db.get_str_dict(
            Namespace.ROLE_CONFIG, RoleKeys.SELF_ASSIGNABLE_ROLE_DESCRIPTIONS
        )

        names: Dict[str, str] = self.db.get_str_dict(
            Namespace.ROLE_CONFIG, RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES
        )

        embed = discord.Embed(
            title="Self-Assignable Roles",
            description="Lists self assignable roles and their descriptions",
        )

        for role_id in role_ids:
            embed.add_field(
                name=names[role_id], value=descriptions[role_id], inline=False
            )
