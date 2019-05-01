import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
import random

import urllib
import urllib.request
import json
from io import StringIO

import discord
from discord.ext import commands
from discord.utils import get


import ffrrace

active_races = dict()
aliases = dict()
teamslist = dict()
allow_races_bool = True
ADMINS = ADMINS = ["Primordial Forces", "Dev Admin"]



def allow_seed_rolling(ctx):
    return (ctx.channel.name == "call_for_races") or (ctx.channel.id in active_races.keys())

def is_call_for_races(ctx):
    return ctx.channel.name == "call_for_races"

def is_race_room(ctx):
    return ctx.channel.id in active_races.keys()

def is_race_started(toggle = True):
    async def predicate(ctx):
        try:
            race = active_races[ctx.channel.id]
        except KeyError:
            return False
        return race.started if toggle else not race.started
    return commands.check(predicate)

def is_runner(toggle = True):
    """
    True is the user is a runner false if a spectator
    :param ctx: context for the command
    :return: bool
    """
    async def predicate(ctx):
        rval = ctx.author.id in aliases[ctx.channel.id].keys()
        return rval if toggle else not rval
    return commands.check(predicate)

def is_team_leader(ctx):
    return ctx.author in teamslist[ctx.channel.id].keys()

def is_race_owner(ctx):
    race = active_races[ctx.channel.id]
    return ctx.author.id == race.owner

def allow_races(ctx):
    return allow_races_bool

def is_admin(ctx):
    user = ctx.author
    return (any(role.name in ADMINS for role in user.roles)) or (user.id == int(140605120579764226))


class Races(commands.Cog):

    def __init__(self, bot, ADMINS):
        self.bot = bot


    @commands.command(aliases=['sr'])
    @commands.check(is_call_for_races)
    @commands.check(allow_races)
    async def startrace(self, ctx, *, name = None):
        if name is None:
            await ctx.author.send("you forgot to name your race")
            return
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        racechannel = await ctx.guild.create_text_channel(name, category=get(ctx.guild.categories, name="races"),
                                      reason="bot generated channel for a race, will be deleted after race finishes")
        race = ffrrace.Race(racechannel.id, name)
        active_races[racechannel.id] = race
        race.role = await ctx.guild.create_role(name=race.id, reason="role for a race")
        race.channel = racechannel
        await racechannel.set_permissions(race.role, read_messages=True, send_messages=True)
        race.message = await ctx.channel.send('join this race with the following ?join command, @ any people that will be on your team if playing coop. Spectate the race with the following ?spectate command\n'
                             + '?join ' + str(racechannel.id) + '\n'
                             + '?spectate ' + str(racechannel.id))
        aliases[racechannel.id] = dict() # for team races
        teamslist[racechannel.id] = dict()
        race.owner = ctx.author.id

    @commands.command(aliases=['cr'])
    @is_race_started(toggle=False)
    @commands.check(is_race_owner)
    @commands.check(is_race_room)
    async def closerace(self, ctx):
        await ctx.channel.send('deleting this race in 5 minutes')
        await self.removeraceroom(ctx, 300)

    @commands.command(aliases=["enter"])
    @commands.check(allow_seed_rolling)
    async def join(self, ctx, id = None, name = None):
        await ctx.message.delete()
        if id is None:
            id = ctx.channel.id
        id = int(id)
        try:
            if active_races[id].started is True:
                ctx.channel.send("that race has already started")
                return
        except KeyError:
            await ctx.author.send("That id doesnt exist")
            return

        if name is None:
            name = ctx.author.display_name

        race = active_races[id]
        await ctx.author.add_roles(race.role)
        race.addRunner(ctx.author.id, name)
        aliases[id][ctx.author.id] = ctx.author.id
        teamslist[id][ctx.author.id] = dict([("name",name), ("members", [ctx.author.display_name])])
        tagpeople = "Welcome! " + ctx.author.mention
        for r in ctx.message.mentions:
            aliases[id][r.id] = ctx.author.id
            teamslist[id][ctx.author.id]["members"].append(r.display_name)
            await r.add_roles(race.role)
            tagpeople += r.mention + " "
        await race.channel.send(tagpeople)




    @commands.command(aliases=['quit'])
    @is_race_started(toggle=False)
    @is_runner()
    @commands.check(is_race_room)
    async def unjoin(self, ctx):
        try:
            race = active_races[ctx.channel.id]
        except KeyError:
            await ctx.author.send("KeyError in unjoin command")
            return

        if race.runners[ctx.author.id]["ready"] is True:
            race.readycount -= 1
        race.removeRunner(ctx.author.id)
        await ctx.channel.send(ctx.author.display_name + " has left the race and is now cheering from the sidelines.")
        del aliases[ctx.channel.id][ctx.author.id]

        try:
            del teamslist[ctx.channel.id][ctx.author.id]
        except KeyError:
            pass
        try:
            for team in teamslist[ctx.channel.id].values():
                if (ctx.author.display_name in team["members"]):
                    team["members"].remove(ctx.author.display_name)
                    break
        except KeyError:
            pass
        await self.startcountdown(ctx)


    @commands.command(aliases=['s'])
    @commands.check(is_call_for_races)
    async def spectate(self, ctx, id):
        try:
            race = active_races[int(id)]
        except KeyError:
            return
        await ctx.message.delete()
        await ctx.author.add_roles(race.role)
        if id:
            await race.channel.send('%s is now cheering you on from the sidelines' % ctx.author.mention)



    @commands.command(aliases=['r'])
    @is_race_started(toggle=False)
    @is_runner()
    @commands.check(is_race_room)
    async def ready(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            race.ready(ctx.author.id)
            await ctx.channel.send(ctx.author.display_name + " is READY! " + str(len(race.runners) - race.readycount) + " remaining.")
        except KeyError:
            ctx.channel.send("Key Error in 'ready' command")
            return
        await self.startcountdown(ctx)


    @commands.command(aliases=['ur'])
    @is_race_started(toggle=False)
    @is_runner()
    @commands.check(is_race_room)
    async def unready(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            race.unready(ctx.author.id)
            await ctx.channel.send(
                ctx.author.display_name + " is no longer READY. " + str(len(race.runners) - race.readycount) + " remaining.")
        except KeyError:
            ctx.channel.send("Key Error in 'ready' command")
            return

    @commands.command(aliases=['e'])
    @commands.check(is_race_room)
    async def entrants(self, ctx):
        try:
            race = active_races[ctx.channel.id]
        except KeyError:
            await ctx.channel.send("Key Error in 'entrants' command")
            return
        rval = "Current Entrants:\n"
        for runner in race.runners.values():
            rval += runner["name"] + ((" ready" if runner["ready"] else " not ready") if not race.started else
                                      (" done" if runner["etime"] != None else " still going")) + "\n"
        await ctx.channel.send(rval)


    @commands.command()
    @is_race_started()
    @is_runner()
    @commands.check(is_race_room)
    async def done(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            msg = race.done(aliases[race.id][ctx.author.id])
            await ctx.channel.send(msg)
            if (all(r["etime"] != None for r in race.runners.values())):
                await self.endrace(ctx, msg)
        except KeyError:
            await ctx.channel.send("Key Error in 'done' command")

    @commands.command(aliases=["unforfeit"])
    @is_race_started()
    @is_runner()
    @commands.check(is_race_room)
    async def undone(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            msg = race.undone(aliases[race.id][ctx.author.id])
            await ctx.channel.send(msg)
        except KeyError:
            await ctx.channel.send("Key Error in 'undone' command")


    @commands.command(aliases=['t'])
    @is_race_started(toggle=False)
    @commands.check(is_race_room)
    async def teams(self, ctx):
        try:
            rstring = "Teams:\n"
            race = active_races[ctx.channel.id]
            for team in teamslist[race.id].values():
                rstring += team["name"] + ":"
                for member in team["members"]:
                    rstring += " " + member + ","
                rstring = rstring[:-1]
                rstring += "\n"
            await ctx.channel.send(rstring)
        except KeyError:
            await ctx.channel.send("Key Error in 'teams' command")

    @commands.command(aliases=['ta'])
    @is_race_started(toggle=False)
    @commands.check(is_team_leader)
    @commands.check(is_race_room)
    async def teamadd(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            for player in ctx.message.mentions:
                aliases[race.id][player.id] = ctx.author.id
                teamslist[race.id][ctx.author.id]["members"].append(player.display_name)
        except KeyError:
            await ctx.channel.send("Key Error in 'teamadd' command")


    @commands.command(aliases=['tr'])
    @is_race_started(toggle=False)
    @commands.check(is_team_leader)
    @commands.check(is_race_room)
    async def teamremove(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            for player in ctx.message.mentions:
                del aliases[race.id][player.id]
                teamslist[race.id][ctx.author.id]["members"].remove(player.display_name)
        except KeyError:
            await ctx.channel.send("Key Error in 'teamremove' command")


    @commands.command()
    @is_race_started()
    @is_runner()
    @commands.check(is_race_room)
    async def forfeit(self, ctx):
        try:
            race = active_races[ctx.channel.id]
            msg = race.forfeit(aliases[race.id][ctx.author.id])
            await ctx.channel.send(msg)
            if (all(r["etime"] != None for r in race.runners.values())):
                await self.endrace(ctx, msg)
        except KeyError:
            await ctx.channel.send("Key Error in the '?sr forfeit' command")

    @commands.command()
    @commands.check(is_call_for_races)
    async def races(self, ctx):
        rval = "Current races:\n"
        for race in active_races.values():
            rval += "name: " + race.name + " - id: " + str(race.id) +"\n"
        await ctx.channel.send(rval)


    async def endrace(self, ctx, msg):
        rresults = get(ctx.message.guild.channels, name="race-results")
        await rresults.send(msg + "\n===================================")
        await ctx.channel.send("deleting this channel in 5 minutes")
        await asyncio.sleep(300)
        await self.removeraceroom(ctx)


    async def startcountdown(self, ctx):
        race = active_races[ctx.channel.id]
        if (race.readycount != len(race.runners)):
            return
        edited_message = "Race: " + race.name + " has started! Join the race room with the following command!\n ?spectate "+str(race.id)
        await race.message.edit(content=edited_message)
        for i in range(10):
            await ctx.channel.send(str(10-i))
            await asyncio.sleep(1)
        await ctx.channel.send("go!")
        race.start()

    async def removeraceroom(self, ctx, time = 0):
        await asyncio.sleep(time)
        race = active_races[ctx.channel.id]
        role = race.role
        channel = race.channel
        del active_races[ctx.channel.id]
        del aliases[channel.id]
        del teamslist[channel.id]
        await channel.delete(reason="bot deleted channel because the race ended")
        await role.delete(reason="bot deleted role because the race ended")




    # Admin Commands

    @commands.command()
    @commands.check(is_admin)
    @is_race_started(toggle=False)
    @commands.check(is_race_room)
    async def forcestart(self, ctx):
        await self.startcountdown(ctx)

    @commands.command()
    @commands.check(is_admin)
    @commands.check(is_race_room)
    async def forceclose(self, ctx):
        await self.removeraceroom(ctx)

    @commands.command()
    @commands.check(is_admin)
    @is_race_started()
    @commands.check(is_race_room)
    async def forceend(self, ctx):
        race = active_races[ctx.channel.id]
        for runner in race.runners.keys():
            if race.runners[runner]["etime"] == None:
                race.forfeit(runner)
        results = race.finishRace()
        await self.endrace(ctx, results)

    @commands.command()
    @commands.check(is_admin)
    @commands.check(is_race_room)
    async def forceremove(self, ctx):
        try:
            race = active_races[ctx.channel.id]
        except KeyError:
            return
        players = ctx.message.mentions
        for player in players:
            await player.remove_roles(race.role)
            race.removeRunner(ctx.author.id)
            del aliases[ctx.channel.id][ctx.author.id]

            try:
                del teamslist[ctx.channel.id][ctx.author.id]
            except KeyError:
                pass
            try:
                for team in teamslist[ctx.channel.id].values():
                    if (ctx.author.display_name in team["members"]):
                        team["members"].remove(ctx.author.display_name)
                        break
            except KeyError:
                pass

    @commands.command()
    @commands.check(is_admin)
    async def toggleraces(self, ctx):
        global allow_races_bool
        allow_races_bool = not allow_races_bool
        await ctx.channel.send("races " +("enabled" if allow_races_bool else "disabled"))
