from discord.ext import commands

import discord
import logging
from typing import *
from ..common import config, checks, text
from ..common.snippits import wait_for_yes_no
from ..common.redis_client import RedisClient, Namespace, RoleKeys


class Roles(commands.Cog):
    def __init__(self, bot, db):
        self.bot: commands.Bot = bot
        self.db: RedisClient = db

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

            current_descriptions = self.db.get_str_dict(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_DESCRIPTIONS,
            )

            new_role_ids = set([str(x.id) for x in roles]).union(
                current_role_ids
            )

            self.db.set_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_IDS,
                new_role_ids,
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
                RoleKeys.ROLE_DESCRIPTIONS,
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
                await ctx.message.delete()
                raise Exception("couldn't find role name: " + role_name)
            roles.append(role)

        async def remove_roles():
            current_role_ids = self.db.get_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_IDS,
            )

            self.db.set_set(
                Namespace.ROLE_CONFIG,
                RoleKeys.ROLE_IDS,
                current_role_ids - set([str(x.id) for x in roles]),
            )

            for x in roles:
                self.db.del_str_dict_item(
                    Namespace.ROLE_CONFIG,
                    RoleKeys.ROLE_DESCRIPTIONS,
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

    @commands.command(aliases=["lsar"])
    @checks.is_admin()
    async def list_roles(self, ctx: commands.Context):
        """
        Lists all self assignable roles.
        ?lsar
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
                    value=description,
                    inline=False,
                )
            except Exception as e:
                logging.warning("Issue in roles.list_roles: " + repr(e))

        await ctx.channel.send(embed=embed)

    @commands.command(aliases=["grp"])
    @checks.is_admin()
    async def generate_role_posts(self, ctx: commands.Context):
        """
        Generates, or regenerates the bot posts in role requests after
        the self assignable roles are updated.
        ?grp
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
            if k in [str(role.id) for role in roles]:
                new_descriptions[k] = v

        await ctx.channel.send(text.cleaning_up_stale_roles)
        logging.info(roles)

        self.db.set_set(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_IDS,
            set([str(role.id) for role in roles]),
        )

        self.db.set_str_dict(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_DESCRIPTIONS,
            new_descriptions,
        )

        current_role_message_ids = set(
            self.db.get_str_dict(
                Namespace.ROLE_CONFIG, RoleKeys.MESSAGE_ID_ROLE_ID_MAP
            ).keys()
        )

        explanation_msg_id = self.db.get_str(
            Namespace.ROLE_CONFIG, RoleKeys.ROLE_REQUEST_EXPLANATION_ID
        )
        if explanation_msg_id:
            current_role_message_ids.add(explanation_msg_id)

        for msg_id in current_role_message_ids:
            try:
                msg = await role_requests_channel.fetch_message(int(msg_id))
                await msg.delete()
            except Exception as e:
                logging.warning(
                    f"The following error occurred in generate_role_posts: {e}"
                )

        role_msg_role_id_mapping: Dict[str, str] = dict()

        explanation = await role_requests_channel.send(
            text.self_assignable_role_message
        )

        self.db.set_str(
            Namespace.ROLE_CONFIG,
            RoleKeys.ROLE_REQUEST_EXPLANATION_ID,
            str(explanation.id),
        )

        for role in roles:
            msg = await role_requests_channel.send(
                text.role_message(role.name, new_descriptions[str(role.id)])
            )
            await msg.add_reaction("✔")
            role_msg_role_id_mapping[str(msg.id)] = str(role.id)

        self.db.set_str_dict(
            Namespace.ROLE_CONFIG,
            RoleKeys.MESSAGE_ID_ROLE_ID_MAP,
            role_msg_role_id_mapping,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ):

        msg_id_role_id_map = self.db.get_str_dict(
            Namespace.ROLE_CONFIG, RoleKeys.MESSAGE_ID_ROLE_ID_MAP
        )

        if (
            str(payload.message_id) in msg_id_role_id_map.keys()
            and payload.user_id != self.bot.user.id
        ):
            guild = self.bot.get_guild(payload.guild_id)
            role = guild.get_role(
                int(msg_id_role_id_map[str(payload.message_id)])
            )

            user = guild.get_member(payload.user_id)
            user_roles = user.roles
            if role not in user_roles:
                await user.add_roles(role)
            else:
                await user.remove_roles(role)

            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)

            await msg.remove_reaction("✔", user)
