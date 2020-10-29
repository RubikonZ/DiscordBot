# -*- coding: utf-8 -*-
import os
import random
import discord
import requests
import requests.auth
import json
import steam
from steam.steamid import SteamID
import datetime
import asyncio
import praw
import re

from discord.ext import commands
from dotenv import load_dotenv

# loads environment variables from a .env file into your shell’s environment variables
load_dotenv('token.env')
TOKEN = os.getenv('DISCORD_TOKEN')
STEAM_KEY = os.getenv('STEAM_KEY')
REDDIT_TOKEN = os.getenv('REDDIT_SECRET')
REDDIT_ID = os.getenv('REDDIT_SCRIPT')
REDDIT_NAME = 'Rubikown'
REDDIT_PW = os.getenv('REDDIT_PW')

# guild = bot.get_guild(330436235103567882)

# http://api.steampowered.com/<interface name>/<method name>/v<version>/?key=<api key>&format=<format>

# Reddit request

bot = commands.Bot(command_prefix='.')


#  Connection to Discord
@bot.event
async def on_ready():
    global json_nickname
    global srvr

    srvr = discord.utils.get(bot.guilds)
    with open("data.json", "r") as openfile:
        json_nickname = json.load(openfile)

    bot_status = discord.Game('WIP bot')  # Sets the status of bots (shows below it's nickname)
    print(f'{bot.user.name} connected to server: \'{srvr.name}\' (id: {srvr.id})')

    await bot.change_presence(status=discord.Status.idle, activity=bot_status)


@bot.event
async def on_member_join(member):
    print(f'{member} has joined \'{srvr.name}\'.')


@bot.event
async def on_member_remove(member):
    print(f'{member} has left \'{srvr.name}\'.')



##### Bot commands
@bot.command(name='purge')
@commands.has_permissions(manage_messages=True, read_message_history=True)
async def purge(ctx, amount: int):
    deleted = await ctx.channel.purge(limit=amount + 1)
    print(f'Deleted last {len(deleted)} messages')
    ddeleted = ctx.channel.send(f'Deleted last {len(deleted)} messages')
    await asyncio.sleep(2)
    await ddeleted.delete()


@bot.command(name='otter')
@commands.cooldown(1, 30, commands.BucketType.user)
async def otter(ctx):
    reddit = praw.Reddit(client_id=REDDIT_ID, client_secret=REDDIT_TOKEN, user_agent="Win10:DiscordBot:v0.0.1 (by u/Rubikown)")
    submission = reddit.subreddit("Otters+Otterable+GifsOfOtters").random()
    print(f'https://old.reddit.com{submission.permalink}')
    await ctx.send(f'{ctx.author.mention} {submission.url}')  # TODO: Add @mention of a person who used the command
    await ctx.message.delete()


@bot.command(name='test')
async def test(ctx):
    print(ctx.me, bot.user)
    print(type(ctx.me), type(bot.user))


@bot.command(name='gdq')  # 16th August 2020, 15.30 UTC
async def gdq(ctx):
    gdq_date = datetime.datetime(2020, 8, 16, 18, 30)  # GDQ Date
    delta = gdq_date - datetime.datetime.now().replace(microsecond=0)

    def strfdelta(fdelta, fmt):
        d = {"days": fdelta.days}
        d["hours"], rem = divmod(fdelta.seconds, 3600)
        d["minutes"], d["seconds"] = divmod(rem, 60)
        return fmt.format(**d)

    # print('SGDQ 2020 starts in:', strfdelta(delta, '{days} days, {hours} hours, {minutes} minutes and {seconds} seconds'))
    # await ctx.send(f"SGDQ 2020 starts in: {strfdelta(delta, '{days} days, {hours} hours, {minutes} minutes and {seconds} seconds')}")
    await ctx.send("https://www.twitch.tv/gamesdonequick")


@bot.command(name='roll_dice', help='Simulates rolling dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [str(random.choice(range(1, number_of_sides + 1))) for _ in range(number_of_dice)]
    await ctx.send(', '.join(dice))


@bot.command(name='ownerid', help='shows owner\'s id')
@commands.is_owner()
async def owner(ctx):
    owner_name = bot.get_user(bot.owner_id)
    await ctx.send(f'```Owner of the bot: {bot.owner_id}, his Discord ID is: {owner_name}```')
    print(f'Owner of the bot: {owner_name}')


@bot.command(name='create-channel')
@commands.is_owner()
async def create_channel(ctx, channel_name: str):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)


@bot.command(name='srvrinfo')
@commands.is_owner()
async def review(ctx):
    if ctx.guild.large:
        print('Server has more than 250 members')
    emoji_list = []
    for ename in ctx.guild.emojis:
        emoji_list.append(ename.name)
    print(f'Server name is: {ctx.guild.name} \n'
          f'Member count: {ctx.guild.member_count} \n'
          f'Members of this server: \n'
          f'Names of emojis on server: {emoji_list}  \n'
          f'The region the server belongs on: {ctx.guild.region} \n')
    await ctx.send(f'```Server name is: {ctx.guild.name} \n'
                   f'Member count: {ctx.guild.member_count} \n'
                   f'Members of this server: \n'
                   f'Names of emojis on server: {emoji_list}  \n'
                   f'The region the server belongs on: {ctx.guild.region}```')


@bot.command(name='usercount')
@commands.is_owner()
async def test(ctx):
    members = []
    for m in ctx.guild.members:
        members.append(m.name)
    print(f'Members: {members}')
    await ctx.send(f'```members```')


@bot.command(name='quit', help='Bot quits until turned back on')
@commands.is_owner()
async def bot_quit(ctx):
    await ctx.send('cya!')
    await bot.close()


#  Потом узнать как обозначаются статусы Busy и Streaming
@bot.command(name='ustatus', help='shows number of members and counts statuses')
@commands.is_owner()
async def ustatus(ctx):
    online = 0
    offline = 0
    idle = 0

    for member in ctx.guild.members:
        if str(member.status) != 'offline':
            online += 1
            if str(member.status) == 'idle':
                idle += 1
        else:
            offline += 1

    print(f'Number of members: {ctx.guild.member_count} \n'
          f'Online: {online}, Offline: {offline}, Idle: {idle}')
    await ctx.send(f'```Number of members: {ctx.guild.member_count} \n'
                   f'Online: {online}, Offline: {offline}, Idle: {idle}```')


# my id 76561197998962090
# https://steamcommunity.com/id/RubikonZ
@bot.command(name='steam_player', help='shows real name and full avatar of given user')
async def steam_player(ctx, steam_url: str):
    nicknames = []

    def steamrequest(nname, skey, steam_id):
        return nname.append(requests.get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={skey}&format=json&steamids={steam_id}'))

    if ',' in steam_url:
        names = steam_url.split(',')
        print(names)
        for name in names:
            steamid = steam.steamid.steam64_from_url(f'https://steamcommunity.com/id/{name}')
            steamrequest(nicknames, STEAM_KEY, steamid)
    elif 'steamcommunity.com' in steam_url:
        steamid = steam.steamid.steam64_from_url('https://steamcommunity.com/id/{}'.format(re.findall("\\w*$", steam_url)[0]))
        # TODO: Check if contains only numbers (id) or if it's nickname
        steamrequest(nicknames, STEAM_KEY, steamid)
        # TODO: Fix so it works when link contains both nicknames and number ids
    else:
        # Implies that
        steamid = steam.steamid.steam64_from_url(f'https://steamcommunity.com/id/{steam_url}')
        print(steamid)
        steamrequest(nicknames, STEAM_KEY, steamid)

    for user in nicknames:
        print(f"Real name: {user.json()['response']['players'][0]['realname']} \n"
              f"Full avatar link: {user.json()['response']['players'][0]['avatarfull']}")
        await ctx.send(f"Real name: {user.json()['response']['players'][0]['realname']} \n"
                       f"Full avatar link: {user.json()['response']['players'][0]['avatarfull']}")


#  Responds to messages (listen)
@bot.listen()
async def on_message(ctx):
    if ctx.author == bot.user:
        return
    if 'Dyno' in ctx.author.name:
        return
    if ctx.content == '':
        return

    # Saving in dictionary amount of messages each user posted
    json_nickname[ctx.author.name] = json_nickname.get(ctx.author.name, 0) + 1  # {'Rubikon': 1}
    with open('data.json', 'w', encoding='utf-8') as writefile:
        json.dump(json_nickname, writefile)

    # Writing logs from all channels into 1 file
    with open('logs\logs.txt', 'a', encoding='utf-8') as logs:
        logs.write(f'[{ctx.created_at.hour + 3}:{ctx.created_at.minute}:{ctx.created_at.second}] '
                   f'#{ctx.channel} <{ctx.author.name}>: {ctx.content}\n')
    # TODO: Can also look for links and put them in separate file
    # TODO: Should find a way to record into separate files

    message_dict = {
        'hour_timestamp': ctx.created_at.hour + 3,
        'minute_timestamp': ctx.created_at.minute,
        'second_timestamp': ctx.created_at.second,
        'channel': ctx.channel.name,
        'author': ctx.author.name,
        'message': ctx.content
    }
    json_message = json.dumps(message_dict, indent=4, ensure_ascii=False)
    with open('logs\logs.json', 'a', encoding='utf-8') as appendfile:
        appendfile.write(json_message)

    ch_id = bot.get_channel(739848000817332285)  # bot_history
    #  +3 - это подгон из UTC в Московское время (желательно найти автоматический способ)
    await ch_id.send(f'[{ctx.created_at.hour + 3}:{ctx.created_at.minute}:{ctx.created_at.second}] '
                     f'#{ctx.channel} <**{ctx.author.name}**>: {ctx.content}')
    # TODO: Change contents of {ctx.content} so that if message has a link, it doesn't show preview

    if ctx.content.startswith('hello'):
        await ctx.channel.send('Hello!')
    elif ctx.content.startswith('(╯°□°）╯︵ ┻━┻'):
        await ctx.channel.send('┬─┬﻿ ノ( ゜-゜ノ)')


# Error check
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have the correct role for this command.')

# Runs bot

bot.run(TOKEN)
