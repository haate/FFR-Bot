from discord.ext import commands

import discord
import logging
from typing import *
from ..common import config, checks, text
from ..common.snippits import wait_for_yes_no
from ..common.redis_client import RedisClient, Namespace, RoleKeys


class Roles(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db: RedisClient = db

    @commands.command(aliases=["ar", "addrole"])
    @checks.is_role_requests_channel()
    async def add_role(self, ctx, *, role=None):
        if role is None:
            await ctx.author.send("you forget to ask for a role")
            await ctx.message.delete()
            return
        role_clean = role.lower().strip("\"'")

        role_names = self.db.get_str_dict(
            Namespace.ROLE_CONFIG,
            RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES,
        )

        if role_clean not in [x.lower() for x in role_names.values()]:
            await ctx.author.send(
                "you cannot give yourself the role: "
                + role
                + "\n or that role doesnt exist"
            )
            await ctx.message.delete()
        else:
            role = ctx.guild.get_role(
                int(
                    [
                        k
                        for k, v in role_names.items()
                        if v.lower() == role_clean
                    ][0]
                )
            )
            await ctx.author.add_roles(role)

    @commands.command(aliases=["rr", "removerole"])
    @checks.is_role_requests_channel()
    async def remove_role(self, ctx, *, role=None):
        if role is None:
            await ctx.author.send("you forget to say which role to remove")
            await ctx.message.delete()
            return
        role_clean = role.lower().strip("\"'")
        role_names = self.db.get_str_dict(
            Namespace.ROLE_CONFIG,
            RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES,
        )
        if role_clean not in [x.lower() for x in role_names.values()]:
            await ctx.author.send(
                "you cannot remove yourself from the role: "
                + role
                + "\n or that role doesnt exist"
            )
            await ctx.message.delete()
        else:
            role = ctx.guild.get_role(
                int(
                    [
                        k
                        for k, v in role_names.items()
                        if v.lower() == role_clean
                    ][0]
                )
            )
            await ctx.author.remove_roles(role)

    @commands.command(aliases=["asar"])
    @checks.is_admin()
    async def add_self_assignable_role(self, ctx: commands.Context, *args):
        """
        Adds to the self assignable roles. ?asar "role name" "description".
        Can add multiple at once.
        """

        guild: discord.Guild = ctx.guild
        descriptions: List[str] = []
        roles: List[discord.Role] = []

        if len(args) % 2 != 0:
            await ctx.author.send(text.add_self_assignable_role_arg_count_off)
            await ctx.message.delete()
            return

        for i in range(len(args) // 2):
            role_name = args[2 * i]
            try:
                role = [
                    role for role in guild.roles if role.name == role_name
                ][0]
            except IndexError:
                await ctx.author.send(
                    'could not find the role named: "' + role_name + '"'
                )
                await ctx.message.delete()
                raise Exception("couldn't find role name: " + role_name)
            roles.append(role)

            descriptions.append(args[2 * i + 1])

        async def add_roles():
            current_role_ids = self.db.get_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_IDS,
            )

            current_role_names = self.db.get_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_NAMES,
            )

            current_descriptions = self.db.get_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_DESCRIPTIONS,
            )

            new_role_ids = set([str(x.id) for x in roles]).union(
                current_role_ids
            )

            self.db.set_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.SELF_ASSIGNABLE_ROLE_IDS,
                new_role_ids,
            )
            role_names = dict([(str(x.id), x.name) for x in roles])

            if current_role_names:
                current_role_names.update(role_names)
                new_role_names = current_role_names
            else:
                new_role_names = role_names
            self.db.set_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES,
                new_role_names,
            )

            description_dict = dict(
                zip([str(x.id) for x in roles], descriptions)
            )

            if current_descriptions:
                current_descriptions.update(description_dict)
                new_descriptions = current_descriptions
            else:
                new_descriptions = description_dict

            self.db.set_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.SELF_ASSIGNABLE_ROLE_DESCRIPTIONS,
                new_descriptions,
            )
            await ctx.channel.send(text.roles_added)

        async def no_change():
            await ctx.channel.send(text.roles_not_added)

        question = text.roles_look_ok_added + "\n"

        for j in range(len(roles)):
            role = roles[j]
            description = descriptions[j]
            question += (
                "\nname: " + role.name + ", description: " + description + "\n"
            )

        await wait_for_yes_no(self.bot, ctx, question, add_roles, no_change)

    @commands.command(aliases=["rsar"])
    @checks.is_admin()
    async def remove_self_assignable_role(self, ctx: commands.Context, *args):
        """
        Removes from the self assignable roles. ?rsar "role name".
        Can remove multiple at once.
        """

        guild: discord.Guild = ctx.guild
        roles: List[discord.Role] = []

        for role_name in args:
            role = [role for role in guild.roles if role.name == role_name][0]
            if role is None:
                await ctx.author.send(
                    'could not find the role named: "' + role_name + '"'
                )
                ctx.message.delete()
                raise Exception("couldn't find role name: " + role_name)
            roles.append(role)

        async def remove_roles():
            current_role_ids = self.db.get_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.SELF_ASSIGNABLE_ROLE_IDS,
            )

            self.db.set_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.SELF_ASSIGNABLE_ROLE_IDS,
                current_role_ids - set([str(x.id) for x in roles]),
            )

            for x in roles:
                self.db.del_str_dict_item(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.SELF_ASSIGNABLE_ROLE_NAMES,
                    str(x.id),
                )
                self.db.del_str_dict_item(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.SELF_ASSIGNABLE_ROLE_DESCRIPTIONS,
                    str(x.id),
                )

            await ctx.channel.send(text.roles_removed)

        async def no_change():
            await ctx.channel.send(text.roles_not_removed)

        question = text.roles_look_ok_removed + "\n"

        for j in range(len(roles)):
            role = roles[j]
            question += "\nname: " + role.name

        await wait_for_yes_no(self.bot, ctx, question, remove_roles, no_change)

    @commands.command(aliases=["lsar", "listroles"])
    async def list_roles(self, ctx: commands.Context):
        """
        Lists all self assignable roles.
        """

        role_ids: Set[str] = (
            self.db.get_set(Namespace.ROLE_CONFIG, RoleKeys.ROLE_IDS) or set()
        )

        descriptions: Dict[str, str] = (
            self.db.get_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_DESCRIPTIONS,
            )
            or dict()
        )

        roles = [ctx.guild.get_role(int(role_id)) for role_id in role_ids]

        names: Dict[str, str] = {
            str(role.id): role.name for role in roles if role is not None
        }

        embed = discord.Embed(
            title="Self-Assignable Roles",
            description="Lists self assignable roles and their descriptions",
        )
        logging.debug(
            "list_roles command"
            + repr(names)
            + repr(roles)
            + repr(descriptions)
            + repr(role_ids)
        )

        for role_id in role_ids:
            try:
                name = names[role_id]
                description = descriptions[role_id]
                embed.add_field(
                    name=name,
                    value=description
                    + "\n\njoin this role with: ?addrole "
                    + name,
                    inline=False,
                )
            except Exception as e:
                logging.warning("Issue in roles.list_roles: " + repr(e))

        embed.colour = 0x0000FF

        await ctx.channel.send(embed=embed)

    @commands.command(aliases=["grp"])
    @checks.is_admin()
    async def generate_role_posts(self, ctx: commands.Context):
        """
        Generates, or regenerates the bot posts in role requests after
        the self assignable roles are updated.
        """

        role_ids: Set[str] = (
            self.db.get_set(Namespace.ROLE_CONFIG, RoleKeys.ROLE_IDS) or set()
        )

        descriptions: Dict[str, str] = (
            self.db.get_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_DESCRIPTIONS,
            )
            or dict()
        )

        role_requests_channel: Optional[
            discord.TextChannel
        ] = ctx.guild.get_channel(config.get_role_requests_channel_id())

        if role_requests_channel is None:
            await ctx.author.send(text.role_requests_channel_not_set)
            await ctx.message.delete()
            return

        roles: List[discord.Role] = []
        new_descriptions: Dict[str, str] = dict()

        for i in range(len(role_ids)):
            role_id = role_ids.pop()
            role = ctx.guild.get_role(int(role_id))
            if role is not None:
                roles.append(role)

        for k, v in descriptions.items():
            if k in [role.id for role in roles]:
                new_descriptions[k] = v

        await ctx.channel.send(text.cleaning_up_stale_roles)

        self.db.set_set(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_IDS,
            set([role.id for role in roles]),
        )

        self.db.set_str_dict(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_DESCRIPTIONS,
            new_descriptions,
        )

        role_request_message_ids = (
            self.db.get_set(
                Namespace.ROLE_CONFIG, RoleKeys.ROLE_REQUEST_MESSAGE_IDS
            )
            or set()
        )

        for msg_id in role_request_message_ids:
            try:
                msg = await role_requests_channel.fetch_message(int(msg_id))
                await msg.delete()
            except Exception as e:
                logging.warning(
                    f"The following error occurred in generate_role_posts: {e}"
                )

        new_role_request_messages: List[discord.Message] = [
            await role_requests_channel.send(text.self_assignable_role_message)
        ]
        logging.info(repr(roles))

        for role in roles:
            new_role_request_messages.append(
                await role_requests_channel.send(
                    role.name + " " + new_descriptions[role.id]
                )
            )

        self.db.set_set(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_REQUEST_MESSAGE_IDS,
            set([str(msg.id) for msg in new_role_request_messages]),
        )
