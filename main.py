import discord 
import os
import random
import pathlib
import json
import youtube_dl
import asyncio
import time
import logging
import queue
import sys
import atexit
import subprocess
from discord.ext import commands, tasks
import inspect
from discord.utils import get
from itertools import cycle

lq = True

rundir = pathlib.Path(__file__,).parent.absolute()
home = os.getenv('HOME')

now = time.gmtime()
start_time = f'{now[0]}_{now[1]}_{now[2]}_{now[3]}_{now[4]}_{now[5]}'
try:
	os.remove(f'{rundir}/logs/latest.log')
except FileNotFoundError:
	print("No latest log.")
finally:
	open(f'{rundir}/logs/{start_time}.log','x')
os.symlink(f'{rundir}/logs/{start_time}.log',f'{rundir}/logs/latest.log')

print(f"Started at {start_time}")
logging.basicConfig(filename=f'{rundir}/logs/latest.log', level=logging.INFO)
logger = logging.getLogger("bot.main")
logger.info(f'Started at {start_time}.')

servers = {}
with open(f'{rundir}/private/servers.json') as f:
	servers = json.load(f)

dnd = {}
with open(f'{rundir}/private/dnd.json') as f:
	dnd = json.load(f)

config = {}
with open(f'{rundir}/private/bot.json') as file:
	config = json.load(file)

responses = {}
with open(f"{rundir}/responselists.json") as file:
	responses = json.load(file)

def parse_duration(duration: int):
	minutes, seconds = divmod(duration, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)

	duration = []
	if days > 0:
		duration.append(f'{days} days')
	if hours > 0:
		duration.append(f'{hours} hours')
	if minutes > 0:
		duration.append(f'{minutes} minutes')
	if seconds > 0:
		duration.append(f'{seconds} seconds')

	return ', '.join(duration)

#grabs server prefix from each server
def get_prefix(client: discord.ext.commands.bot.Bot, message: discord.Message):
	if message.channel.type.value == 1:
		return '.'
	if not servers[str(message.guild.id)].get('prefix'):
		return '~'
	else:
		return servers[str(message.guild.id)].get('prefix')

#Set bot command prefix!
client = commands.Bot(command_prefix = get_prefix)

client.remove_command('help')
status = cycle(['help - Brings up commands', 'aboutme - Shows bot info', 'trivia - Fun facts!', 'changeprefix - Customise server prefix!','Ping me to get prefix on the server'])


#Various debug console message events
@client.event
async def on_connect():
	logger.info('Connected to discord...')

@client.event
async def on_disconnect():
	logger.info('Disconnected from discord.')

@client.event
async def on_ready():
	#set status, change activity and print ready and start loop
	change_status.start()
	hail_theOwner.start()
	await client.change_presence(status=discord.Status.online, activity=discord.Game('~helpme for commands!'))
	logger.info(f'Logged in as {client.user.name}')
	logger.info(f'Client ID: {client.user.id}')
	logger.info('---------')
	print("Ready")

@client.command(name='dummy_log')
async def dummy_log(ctx: discord.ext.commands.Context):
	attempt_id = ctx.author.id
	if attempt_id == 465816879072542720 or attempt_id == 437296242817761292: #first id is mulfok, second is lenrik
		logger.debug("dummy debug log message")
		logger.info("dummy info log message")
		logger.warning("dummy warning log message")
		logger.error("dummy error log message")
		logger.critical("dummy critical log message")
		print("dummy message terminal")
		print("another message but\nspilt\ninto lines.")
		message = await ctx.send("debug log created")
		await asyncio.sleep(1)
		await message.delete()
	await ctx.message.delete()

#Set default command prefix on server join
@client.event
async def on_guild_join(guild):
	logger.info(f'Bot joined {guild.name} (ID: {guild.id})')
	with open(f'{rundir}/private/servers.json', 'r') as f:
		servers = json.load(f)

	servers[str(guild.id)]["prefix"] = '~'
	globals()["servers"] = servers

	with open(f'{rundir}/private/servers.json', 'w') as f:
		json.dump(servers, f, indent=2)

#Purge command prefix upon server leave
@client.event
async def on_guild_remove(guild):
	logger.info(f'Bot left {guild.name} (ID: {guild.id})')
	with open(f'{rundir}/private/servers.json', 'r') as f:
		servers = json.load(f)

	servers.pop(str(guild.id))
	globals()["servers"] = servers

	with open(f'{rundir}/private/servers.json', 'w') as f:
		json.dump(servers, f, indent=2)

@client.command(aliases=["setprefix"])
async def changeprefix(ctx: discord.ext.commands.Context, prefix):
	if ctx.author.guild_permissions.administrator or ctx.author.id == 437296242817761292:
		with open(f'{rundir}/private/servers.json', 'r') as f:
			servers = json.load(f)

		logger.info(f'Prefix changed to {prefix} for server {ctx.guild.name} (ID {ctx.guild.id})')
		servers[str(ctx.guild.id)]['prefix'] = prefix
		servers[str(ctx.guild.id)]['name'] = str(ctx.guild.name)
		await ctx.send(f'Prefix changed to `{prefix}`! :white_check_mark:')
		globals()["servers"] = servers

		with open(f'{rundir}/private/servers.json', 'w') as f:
			json.dump(servers, f, indent=2)
	else:
		commands.MissingPermissions()

@client.command(name="set")
async def setParam(ctx: discord.ext.commands.Context, param: str, *value: str):
	if (param == "channel"):
		if ctx.author.guild_permissions.administrator or ctx.author.id == 437296242817761292:
			if len(value) < 1:
				raise commands.MissingRequiredArgument(inspect.Parameter(name="chat",kind=inspect._ParameterKind.VAR_POSITIONAL))
			if len(value) < 2:
				raise commands.MissingRequiredArgument(inspect.Parameter(name="room",kind=inspect._ParameterKind.VAR_POSITIONAL))
			channel = ctx.channel
			try:
				chan_id = int(value[1][2:-1])
				channel = ctx.guild.get_channel(chan_id)
			except ValueError:
				if value[1] == "here":
					if servers[f'{ctx.guild.id}'].get("channels") == None:
						servers[f'{ctx.guild.id}']["channels"] = {}
					servers[f'{ctx.guild.id}']["channels"][value[0]] = channel.id
					message = await ctx.send(f"Channel {value[0]} has been set to #{channel} for this guild.")
					await asyncio.sleep(3)
					await asyncio.gather(message.delete(),ctx.message.delete())
					print(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
					logger.info(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
				elif value[1] == "unset":
					if servers[f'{ctx.guild.id}'].get("channels") == None:
						message = await ctx.send("No channels are set for this guild.")
						await asyncio.sleep(3)
						await asyncio.gather(message.delete(),ctx.message.delete())
						return
					elif servers[f'{ctx.guild.id}']["channels"].get(value[0]) == None:
						message = await ctx.send("This channel is not set for this guild.")
						await asyncio.sleep(3)
						await asyncio.gather(message.delete(),ctx.message.delete())
						return
					else:
						servers[f'{ctx.guild.id}']["channels"][value[0]] = None
						message = await ctx.send(f"Channel {value[0]} has successfully unset for this guild.")
						await asyncio.sleep(3)
						await asyncio.gather(message.delete(),ctx.message.delete())
						print(f"Channel {value[0]} has been unset for guild {ctx.guild}.")
						logger.info(f"Channel {value[0]} has been unset for guild {ctx.guild}.")
				else:
					print(f'not setting chat {chat} to anywhere as invalid parameters are passed in.')
			else:
				if servers[f'{ctx.guild.id}'].get("channels") == None:
					servers[f'{ctx.guild.id}']["channels"] = {}
				servers[f'{ctx.guild.id}']["channels"][value[0]] = chan_id
				message = await ctx.send(f"Channel {value[0]} has been set to #{channel} for this guild.")
				await asyncio.sleep(3)
				await asyncio.gather(message.delete(),ctx.message.delete())
				print(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
				logger.info(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
			with open(f'{rundir}/private/servers.json', 'w') as f:
				json.dump(servers, f, indent=2)

		else:
			commands.MissingPermissions(discord.permissions.Permissions(permissions=8))
	else:
		print(param)

def roll_one(dice: int):
	return random.randrange(dice) + 1

def roll(dices: int, dice: int, keep: int):
	rolls = [roll_one(dice) for i in range(dices)]
	rolls.sort()
	rolls = rolls[len(rolls) - keep:]
	return rolls

def get_stat():
	rolled = roll(4, 6, 3)
	stat = 0
	for i in range(3):
		stat += rolled[i]
	return f"{stat}({int((stat+1)/2)-5})"

@client.command()
async def dnd(ctx: discord.ext.commands.Context, command: str, args):
	if not servers[f'{ctx.guild.id}'].get("channels") == None:
		if not servers[f'{ctx.guild.id}'].get("channels").get("dnd") == None:
			if not servers[f'{ctx.guild.id}']["channels"]["dnd"] == ctx.channel.id:
				ctx.message.content = get_prefix(None,ctx.message) + " in_this_channel"
				raise commands.CommandNotFound()
	if command == "dice":
		i = int(args)
		if i < 1:
			raise commands.BadArgument(' "whole positive nuber', "Unable to throw imaginary dice")
		j = random.randrange(i) + 1
		await ctx.send(f'your number is: {j}')
	elif command == "roll" and args.split()[0] == "stats":
		embed = discord.Embed()
		embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
		embed.add_field(name = "first stat", value = get_stat())
		embed.add_field(name = "second stat", value = get_stat())
		embed.add_field(name = "third stat", value = get_stat())
		embed.add_field(name = "fourth stat", value = get_stat())
		embed.add_field(name = "fifth stat", value = get_stat())
		embed.add_field(name = "sixth stat", value = get_stat())
		await ctx.send(embed=embed)
		
@client.event
async def on_member_join(member):
	logger.info(f'{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')
	print(f'{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')

@client.event
async def on_member_remove(member):
	logger.info(f'{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')
	print(f'{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')

#Tasks Area
@tasks.loop(seconds=5)
async def change_status():
	await client.change_presence(activity=discord.Game(next(status)))

@tasks.loop(seconds=10)
async def hail_theOwner():
	for guild in client.guilds:
		if servers[f'{guild.id}'].get('hail_enabled'):
			if not servers[f'{guild.id}']["channels"] == None:
				if not servers[f'{guild.id}']["channels"]["hail"] == None: 
					if random.randint(0, 999) == 0:
						for text_channel in guild.text_channels:
							if text_channel.id == int(servers.get(f'{guild.id}').get("hail_channel")):
								await text_channel.send(f"Hail the great {guild.owner.name}, owner of this discord!")

#Commands area
@client.command()
async def ping(ctx):
	#simply reply with 'Pong!' and milliseconds
	await ctx.send(f'Pong! {round(client.latency*1000)}ms')

@client.command(name="commands")
async def c(ctx):
	result = "\n"
	await ctx.send(result.join(client.all_commands.keys()))

@client.command(name="toggle")
async def toggle(ctx: discord.ext.commands.Context, command: str):
	if command == "pingcamp":
		is_camp = ctx.author.id == 138408730705264640
		enabled = globals()['config']['pingcamp_enabled']
		camp_or_enabled = is_camp or enabled
		if camp_or_enabled:
			globals()['config']['pingcamp_enabled'] = not globals()['config']['pingcamp_enabled']
			with open(f'{rundir}/private/bot.json', 'w') as file:
				config = json.dump(file)
		else:
			await ctx.send("That's not how it works, you can't decide whether	 you can annoy Camp just because, only Camp can :P")

@client.command(name="pingcamp")
async def no(ctx: discord.ext.commands.Context, pings: int = 1, delay: float = 1):
	if config['pingcamp_enabled']:
		initial_pings = pings
		logger.warning(f"{ctx.author.name} (ID: {ctx.author.id}) requested to ping camp {pings} times with delay of {delay} seconds.")
		while pings > 0:
			pings -= 1
			if stop_pings:
				await ctx.send(f"<@138408730705264640>, pings were stopped.")
			elif pings > 0:
				await asyncio.sleep(delay)
				await ctx.send(f"<@138408730705264640>, ping № {initial_pings-pings} out of {initial_pings} (ETA:{parse_duration(int(delay*pings))})")
			else:
				await ctx.send(f"<@138408730705264640>, ping № {initial_pings-pings}. **last ping**.")
	else:
		await ctx.send("This command was disabled, but Camp can turn it on if he wants.")

@client.command(name="pingzeek")
async def no(ctx: discord.ext.commands.Context, pings: int = 1, delay: float = 1):
	# if config['pingcamp_enabled']:
	if True:
		initial_pings = pings
		logger.warning(f"{ctx.author.name} (ID: {ctx.author.id}) requested to ping Zeek {pings} times with delay of {delay} seconds.")
		while pings > 0:
			pings -= 1
			if pings > 0:
				await asyncio.sleep(delay)
				await ctx.send(f"<@719431242910793779>, ping № {initial_pings-pings} out of {initial_pings} (ETA:{parse_duration(int(delay*pings))})")
			else:
				await ctx.send(f"<@719431242910793779>, ping № {initial_pings-pings}. **last ping**.")
	else:
		await ctx.send("This command was disabled, but Camp can turn it on if he wants.")

@client.command()
async def pingtrue(ctx):
	#reply with "pong!" and DON'T round ms
	await ctx.send(f'Pong! {client.latency*1000}ms')

#the F command
@client.command()
async def f(ctx):
	#send image link
	fauthor = ctx.message.author

	fembed = discord.Embed(
		colour = discord.Colour.red()
	)
	fembed.set_author(name="Paying respects...")
	fembed.set_image(url=f"{random.choice(responses['f'])}")

	await ctx.send(embed=fembed)

#Random Anime Song Command
@client.command(aliases=["animesong"])
async def randomanimesong(ctx):
	await ctx.send(f"The developers are not weebs I swear :eyes:\n{random.choice(responses['anime'])}")

@client.command(name='8ball',aliases=['eightball'])
async def _8ball(ctx, *, question):
	#output random answer
	await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses["8ball"])}')

@client.command()
async def trivia(ctx):
	#output random answer
	await ctx.send(f'{random.choice(responses["trivia"])}')

@client.command()
async def help(ctx):
	author = ctx.message.author
	message = ctx.message

	helpembed = discord.Embed(
		colour = discord.Colour.red()
	)
	helpembed.set_author(name="Default Bot Prefix: ~")
	helpembed.add_field(name="help", value="Shows the command menu to you.", inline=False)
	helpembed.add_field(name="ping", value="Returns your ping in milliseconds.", inline=False)
	helpembed.add_field(name="pingtrue", value="Returns your ping in milliseconds *without* rounding.", inline=False)
	helpembed.add_field(name="8ball/eightball [question]", value="A Magic Eight Ball Simulator.", inline=False)
	helpembed.add_field(name="clear [number]", value="Clears a set amount of messages, more than -1 and less than 101. (Requires manage messages permission)", inline=False)
	helpembed.add_field(name="aboutme", value="Shows bot info", inline="False")
	helpembed.add_field(name="kick [member]", value="Kicks a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="ban [member]", value="Bans a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="unban [member]", value="Unbans a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="close/exit/quit/stop", value="Shuts the bot down. (Developer-Only Command)", inline=False)
	helpembed.add_field(name="minesweeper [columns] [rows] [bombs]", value="Starts up a game of spoiler-based Minesweeper. (If args left empty, game will start with random settings)", inline=False)
	helpembed.add_field(name="mcmd [page]", value="Pulls up complete Minecraft 1.15.2 command documentation.", inline=False)
	helpembed.add_field(name="trivia", value="Random facts about the developer and interesting things!", inline=False)
	helpembed.add_field(name="slap [person]", value="Slap whoever you choose!", inline=False)
	helpembed.add_field(name="changeprefix [prefix]", value="Changes server prefix. (Requires admin permission)", inline=False)
	helpembed.add_field(name="f", value="Sends a random image of the letter F.", inline=False)
	helpembed.add_field(name="randomanimesong", value="Sends a random anime song.", inline=False)
	helpembed.add_field(name="github", value="Private messages github link. (Developer only command)", inline=False)
	helpembed.add_field(name="todo", value="Private messages bot to-do list. (Developer only command)", inline=False)
	helpembed.add_field(name="joke", value="Tells a joke!", inline=False)
	helpembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/720598695191511110/721769409139703938/OmenaLogo.png")

	await message.delete()
	await ctx.send(embed=helpembed)

@client.command()
async def mcmd(ctx: discord.ext.commands.Context, *, page:int=1):
	mcauthor = ctx.message.author

	mcmdembed = discord.Embed(
		colour=discord.Colour.red(),
		author='1.15.2 Full Command Documentation Page' 
	)
	if   page == 1:
		mcmdembed.set_footer(name="1/4")
		mcmdembed.add_field(name="/advancement", value="Gives, removes, or checks player advancements. [See offical documentation.](https://minecraft.gamepedia.com/Commands/advancement)", inline=False)
		mcmdembed.add_field(name="/ban <name> [<reason>]", value="Adds player to banlist.", inline=False)
		mcmdembed.add_field(name="/ban-ip [<address>|<name>] [<reason>]", value="Adds IP address to banlist.", inline=False)
		mcmdembed.add_field(name="/banlist [ips|players]", value="Displays banlist.", inline=False)
		mcmdembed.add_field(name="/bossbar", value="Creates and modifies bossbars. [See official documentation](https://minecraft.gamepedia.com/Commands/bossbar)", inline=False)
		mcmdembed.add_field(name="/clear [<targets>] [<item>] [<maxCount>]", value="Clears items from player inventory.", inline=False)
		mcmdembed.add_field(name="/clone <x1> <y1> <z1> <x2> <y2> <z2> <x> <y> <z> [maskMode] [cloneMode] [TileName] [dataValue|state]", value="Copies blocks from one place to another.", inline=False)
		mcmdembed.add_field(name="/data", value="Gets, merges, modifies and removes block entity and entity NBT data. [See official documentation](https://minecraft.gamepedia.com/Commands/data)", inline=False)
		mcmdembed.add_field(name="/datapack", value="Controls loaded datapacks. [See official documentation](https://minecraft.gamepedia.com/Commands/datapack)", inline=False)
		mcmdembed.add_field(name="/debug (start|stop|report)", value="Starts or stops a debugging session.", inline=False)
		mcmdembed.add_field(name="/defaultgamemode <mode>", value="Sets the default game mode.", inline=False)
		mcmdembed.add_field(name="/deop <player>", value="Revokes operator status from a player.", inline=False)
		mcmdembed.add_field(name="/difficulty [<difficulty>]", value="Sets the difficulty level.", inline=False)
		mcmdembed.add_field(name="/effect give <entity> <effect> [<seconds>] [<amplifier>] [<hideParticles>]", value="Apply status effect(s).", inline=False)
		mcmdembed.add_field(name="/effect clear <entity> [<effect>]", value="Remove status effect(s).", inline=False)
		mcmdembed.add_field(name="/enchant <player> <enchantment ID> [level]", value="Enchants a players item.", inline=False)
		mcmdembed.add_field(name="/execute", value="Executes another command. [See official documentation](https://minecraft.gamepedia.com/Commands/execute)", inline=False)
		mcmdembed.add_field(name="/fill <x1> <y1> <z1> <x2> <y2> <z2> <block> [destroy|hollow|keep|outline|replace]", value="Fills a region with a specific block.", inline=False)
		mcmdembed.add_field(name="/forceload add <x1> <z1> [<x2> <z2>]", value="Forces a chunk to be constantly loaded.", inline=False)
		mcmdembed.add_field(name="/forceload remove <x1> <z1> [<x2> <z2>]", value="Removes a force-loaded chunk", inline=False)
		mcmdembed.add_field(name="/forceload reomve all", value="Removes all for-loaded chunks.", inline=False)
		mcmdembed.add_field(name="/forceload query [<x1> <z1>]", value="Tells you if specified chunk is force-loaded.", inline=False)
		mcmdembed.add_field(name="/function <function>", value="Runs a function", inline=False)
		mcmdembed.add_field(name="/gamemode <mode> [player]", value="Sets a player's game mode.", inline=False)
		mcmdembed.add_field(name="/gamerule <rule name> [value]", value="Sets or queries a game rule value.", inline=False)
	elif page == 2:
		mcmdembed.set_author(name="1.15.2 Full Command Documentation Page 2/4")
		mcmdembed.add_field(name="/give <player> <item>[<NBT>] [<count>]", value="Gives an item to a player.", inline=False)
		mcmdembed.add_field(name="/help [<command>]", value="Provides help for commmands.", inline=False)
		mcmdembed.add_field(name="/kick <player> [reason]", value="Kicks a player off a server", inline=False)
		mcmdembed.add_field(name="/kill [<targets>]", value="Kills entities.", inline=False)
		mcmdembed.add_field(name="/list [uuids]", value="Lists players on the server.", inline=False)
		mcmdembed.add_field(name="/locate <StructureType>", value="Locates the closest structure.", inline=False)
		mcmdembed.add_field(name="/loot <target> <source>", value="Drops itesm from an inventory slot onto the ground.", inline=False)
		mcmdembed.add_field(name="/me <action>", value="Displays a message about the sender.", inline=False)
		mcmdembed.add_field(name="/tell or /msg or /w <player> <message>", value="Displays a private message to other players.", inline=False)
		mcmdembed.add_field(name="/op <player>", value="Grants operator status to a player.", inline=False)
		mcmdembed.add_field(name="/pardon <player>", value="Removes entries from the banlist.", inline=False)
		mcmdembed.add_field(name="/pardon-ip <address>", value="Removes entries from the banlist.", inline=False)
		mcmdembed.add_field(name="/particle <name> [<pos>] [<delta>] <speed> <count> [<mode>] [<viewers>]", value="Creates particles.", inline=False)
		mcmdembed.add_field(name="/playsound <sound> <source> <player> [x] [y] [z] [volume] [pitch] [minimumVolume]", value="Plays a sound.", inline=False)
		mcmdembed.add_field(name="/publish [port]", value="Opens single-player world to local network.", inline=False)
		mcmdembed.add_field(name="/recipe <give|take> [player] <name|*>", value="Gives or takes player recipes.", inline=False)
		mcmdembed.add_field(name="/reload", value="Reloads loot tables, advancements, and functions from disk.", inline=False)
		mcmdembed.add_field(name="/replaceitem block <x> <y> <z> <slot> <item> [amount]", value="Replaces items in inventories.", inline=False)
		mcmdembed.add_field(name="/replaceitem entity <selector> <slot> <item> [amount]", value="Replaces items in inventories.", inline=False)
		mcmdembed.add_field(name="/save-all [flush]", value="Saves the server to disk.", inline=False)
		mcmdembed.add_field(name="/save-off", value="Disables automatic server saves.", inline=False)
		mcmdembed.add_field(name="/save-on", value="Enables automatic server saves.", inline=False)
		mcmdembed.add_field(name="/say <message>", value="Displays a message to multiple players.", inline=False)
		mcmdembed.add_field(name="/schedule function <function> <time> [append|replace]", value="Delays the execution of a function.", inline=False)
		mcmdembed.add_field(name="/schedule clear <function>", value="Clears a scheduled function.", inline=False)
	elif page == 3:
		mcmdembed.set_author(name="1.15.2 Full Command Documentation Page 3/4")
		mcmdembed.add_field(name="/seed", value="Displays the world seed.", inline=False)
		mcmdembed.add_field(name="/setblock", value="Changes a block to another block. [See official documentation](/schedule clear <function>)", inline=False)
		mcmdembed.add_field(name="/setidletimeout <minutes until kick>", value="Sets the time before idle players are kicked.", inline=False)
		mcmdembed.add_field(name="/setworldspawn [<x> <y> <z>]", value="Sets the world spawn.", inline=False)
		mcmdembed.add_field(name="/spawnpoint [<player>] [<x> <y> <z>]", value="Sets the spawn point for a player.", inline=False)
		mcmdembed.add_field(name="/spectate [target] [player]", value="Make one player in spectator mode spectate an entity.", inline=False)
		mcmdembed.add_field(name="/spreadplayers <x> <z> <spreadDistance> <maxRange> <respectTeams> <player>", value="Teleoprts entities to random locations.", inline=False)
		mcmdembed.add_field(name="/stop", value="Stops a server.", inline=False)
		mcmdembed.add_field(name="/stopsound <player> [<source>] [<sound>]", value="Stops a sound.", inline=False)
		mcmdembed.add_field(name="/summon <entity_name> [<pos>] [<nbt>]", value="Summons an entity.", inline=False)
		mcmdembed.add_field(name="/tag <targets> add <name>", value="Adds an entity tag.", inline=False)
		mcmdembed.add_field(name="/tag <targets> remove <name>", value="Removes an entity tag.", inline=False)
		mcmdembed.add_field(name="/tag <targets> list", value="Lists all entity tags.", inline=False)
		mcmdembed.add_field(name="/team", value="Controls teams. [See official documentation](/tag <targets> list)", inline=False)
		mcmdembed.add_field(name="/teammsg <message>", value="Specifies the message to send to the team.", inline=False)
		mcmdembed.add_field(name="/tp or /teleport", value="Teleports entities. [See offical documentation](https://minecraft.gamepedia.com/Commands/tp)", inline=False)
		mcmdembed.add_field(name="/tellraw <player> <raw json message>", value="Displays a JSON message to players.", inline=False)
		mcmdembed.add_field(name="/time <add|query|set> <value>", value="Changes or queries the world's game time.", inline=False)
		mcmdembed.add_field(name="/title", value="Manages screen titles. [See offical documentation](https://minecraft.gamepedia.com/Commands/title)", inline=False)
		mcmdembed.add_field(name="/trigger <objective> [<add|set> <value>]", value="Sets a trigger to be activated.", inline=False)
		mcmdembed.add_field(name="/weather <clear|rain|thunder> [duration]", value="Sets the weather.", inline=False)
		mcmdembed.add_field(name="/whitelist add <player>", value="Adds a player to whitelist.", inline=False)
		mcmdembed.add_field(name="/whitelist remove <player>", value="Removes a player from whitelist.", inline=False)
		mcmdembed.add_field(name="/whitelist [on|off|list|reload]", value="Manages server whitelist.", inline=False)
		mcmdembed.add_field(name="/worldborder", value="Manages the world border. [See official documentation](/worldborder)", inline=False)
		mcmdembed.add_field(name="/xp [add|set] <players> <amount> [points|levels]", value="Adds or removes player experience.", inline=False)
		mcmdembed.add_field(name="/xp query <player> <amount> [points|levels]", value="Displays a player's current experience.", inline=False)
	elif page == 4:
		mcmdembed.set_author(name="1.15.2 Full Command Documentation Page 4/4")
		mcmdembed.add_field(name="/xp [add|set] <players> <amount> [points|levels]", value="Adds or removes player experience.", inline=False)
		mcmdembed.add_field(name="/xp query <player> <amount> [points|levels]", value="Displays a player's current experience.", inline=False)
	else:
		await ctx.send(f"Sorry, there's no page №{page}")
		return

	await ctx.send(embed=mcmdembed)

@client.command()
async def clear(ctx: discord.ext.commands.Context, amount: int):
	perms = ctx.message.author.permissions_in(ctx.channel)
	if perms.manage_messages or ctx.author.id == 437296242817761292:
		message = ctx.message
		if amount < 0:
			error = await ctx.send("That's not a valid arguement! :x:")
			await asyncio.sleep(1)
			await asyncio.gather(message.delete(), error.delete())
		elif amount > 100:
			error = await ctx.send("Purge limit is 100! :x")
			await asyncio.sleep(1)
			await asyncio.gather(message.delete(), error.delete())
		else:
			await ctx.channel.purge(limit=amount+1)
			await asyncio.sleep(0.1)
			success = await ctx.send(f"Removed {amount} messages! :white_check_mark:")
			await asyncio.sleep(1)
			await success.delete()
	else:
		commands.MissingPermissions()

@client.command()
async def aboutme(ctx):
	await ctx.send("```\nOmena!BOT v1.0.0\n" + \
				   "Developed by:\n" + \
				   "MulfoK: Lead Programmer\n" + \
				   "lenrik1589: Debugger\n" + \
				   "General Purpose Discord Bot\n" + \
				   "Written in Python 3.8.2\n" + \
				   "help for commands list (~ is default prefix)```")

@client.command()
#set params and kick
async def kick(ctx, member: discord.Member, *, reason=None):
	perms = ctx.message.author.permissions_in(ctx.channel)
	if perms.administrator or ctx.author.id == 437296242817761292:
		logger.critical(f'{member.mention} (ID {member.id}) was kicked from server {ctx.guild.id} with reason: "{reason}".')
		await member.kick(reason=reason)
		await ctx.send(f'{member.mention} was kicked from the server. :hammer:')
	else:
		commands.MissingPermissions()

@client.command()
@commands.has_permissions(administrator=True)
#set params and BAN
async def ban(ctx, member : discord.Member, *, reason=None):
	logger.critical(f'{member.mention} (ID {member.id}) was banned from server {ctx.guild.id} with reason: "{reason}".')
	await member.ban(reason=reason)
	await ctx.send(f'{member.mention} was banned from the server. :hammer:')

@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
	#grab server ban list and return
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

		if (user.name, user.discriminator) == (member_name, member_discriminator):
			logger.critical(f'{member.mention} (ID {member.id}) was unbanned from server {ctx.guild.id}.')
			await ctx.guild.unban(user)
			await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
			return

#Developer Commands
##################################################################
#stops bot command
@client.command(aliases=["quit", "exit"])
#@commands.has_permissions(administrator=True)
async def close(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 465816879072542720 or attempt_id == 437296242817761292: #first id is mulfok, second is lenrik
		message = await ctx.send("Shutting down... See ya! :lock:")
		await asyncio.sleep(0.5)
		await asyncio.gather(
			ctx.message.delete(),
			message.delete())
		await client.close()
		logger.info(f'Bot Closed By {ctx.author.name} ID: {ctx.author.id}')
		print(f'Bot Closed By Developer: {ctx.author.name} ID: {ctx.author.id}')

	else:
		logger.info(f"{ctx.author} (ID:{ctx.author.id}) tried to close the bot in {ctx.guild.name}#{ctx.channel}!")
		await ctx.send("You're not a developer! :x:")
		print(f"{ctx.author} (ID: {ctx.author.id}) tried to close the bot!")

#github link command (useful for if you lost the link or something)
@client.command()
async def github(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 437296242817761292 or attempt_id == 465816879072542720 or attempt_id == 691668587005607957 or attempt_id == 634189650608652310: #first id is lenrik, second is mulfok, third is wullie, fourth is brady
		await ctx.author.send("Github (Private): https://github.com/MulfoK/omenabot1.0\nShh... Let's not leak our hard work!")
		message = await ctx.send("You have been private messaged the github link. :white_check_mark:")
		logger.info(f"Github pulled up by {ctx.author} ID: {ctx.author.id}")
		await asyncio.sleep(1)
		await ctx.message.delete()
		await message.delete()

	else:
		await ctx.send("You're not a developer! :x:")
		logger.info(f"{ctx.author} (ID {ctx.author.id}) tried to pull up github link!")

#todo command
@client.command()
async def todo(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 437296242817761292 or attempt_id == 465816879072542720 or attempt_id == 691668587005607957 or attempt_id == 634189650608652310: #first id is mulfok, second is lenrik, third is wullie, fourth is brady
		await ctx.author.send("I feel sorry for you developers...\n" + \
							  "```Our epic todo list:\n" + \
							  "1: Move music.py contents into bot.py\n" + \
							  "2: Get the ~calc command working properly\n```"
							 )
		await ctx.send("The developer to-do list has been private messaged to you! :white_check_mark:")
		logger.info(f"Todo list pulled up by {ctx.author} ID: {ctx.author.id}")

	else:
		await ctx.send("You're not a developer! :x:")
		logger.info(f"{ctx.author} (ID: {ctx.author.id}) tried to pull of the developer to-do list!")
#######################################################
#calc command
@client.command()
async def calc(ctx: discord.ext.commands.Context, *equation: str):
	equation = "".join(equation)
	result = 0
	try:
		result = eval(equation)
	except NameError:
		result = "error evaluating your expression:\n\tuse of varables is not implemented."
		await ctx.send(result)
	print(result)
	#joint = ctx.message.content[len(get_prefix('',ctx)) + 4:].replace(' ', '')
	#if not joint.isascii():
		#await ctx.send("{servers[str(ctx.guild.id)])}calc only accepts ASCII characters as input!")
		#return
	#elif len(joint.replace(["+", "-", "/", '\\',' % ',' ^ ',' * '],' ')) < 1:
		#await ctx.send(f'There should be at least one digit! :x:')
		#return
	equation = equation.replace("*","\*")
	await ctx.send(f"{equation} = {result}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#easter egg commands
#alcohol command
@client.command()
async def alcohol(ctx):
	if ctx.author.id == 397573419811602442: #karnage 397573419811602442
		await ctx.seyound("Go drink alcohol you madman. :beer:")

	else:
		await ctx.send("This command isn't for you! :x:")

#coffee command
@client.command()
async def coffee(ctx):
	if ctx.author.id == 721045183982207046: #lenrick 721045183982207046
		await ctx.send("Go drink coffee you madman. :coffee:")

	else:
		await ctx.send("This command isn't for you! :x:")

#ifstatment command
@client.command(name="if")
async def _if(ctx):
	if ctx.author.id == 465816879072542720:
		await ctx.send("Go learn if statments you madman. :dagger:")

	else:
		await ctx.send("This command isn't for you! :x:")

#hack command
@client.command()
async def hack(ctx, *, hackvic):
	message:discord.Message = ctx.message
	#store homework amount in temp variable
	homeworkstorage = random.choice(responses["hack"]["homework"])
	#send messages in a timely order
	hack_message = await ctx.send(f"Hacking {hackvic}...")
	await asyncio.gather(asyncio.sleep(2),message.delete())
	await hack_message.edit(content=f"Grabbing {homeworkstorage} 'Homework' folder...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f'Selling data to {random.choice(responses["hack"]["companies"])}...')
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Payment recieved: {random.choice(responses['hack']['payment'])}")
	await asyncio.sleep(2)
	await hack_message.edit(content="Bypassing Discord security...")
	await asyncio.sleep(2)
	mail_before, mail_after = random.choice(responses['hack']['mail_body'])
	await hack_message.edit(content=f"Email: {mail_before}{hackvic}{mail_after}@{random.choice(responses['hack']['mail_provider'])}\nPassword: ihateyouihateyougodie")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Reporting {hackvic} for breaking Discord TOS...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Laughing evilly...")
	await asyncio.sleep(2)
	await ctx.send(f"The 100% real hack of {hackvic} is complete.")
	await ctx.send(f"Homework folder size: {homeworkstorage}")

@client.command()
async def slap(ctx, *, person: discord.User):
	await ctx.send(f"Slapped {person}!")

#joke command
@client.command()
async def joke(ctx):
	joke, punchline = random.choice(responses["jokes"])
	message = await ctx.send(joke)
	await asyncio.sleep(2)
	await message.edit(content=joke+"\n"+punchline)

#-----------------------------------
# emergency command
@client.event
async def on_message(message: discord.Message):
	if message.channel.type.name == 'private':
		if not message.author == client.user:
			result = await client.process_commands(message)
			await message.delete()
			message = await message.channel.send("I'm a bot, and certanly not smart enough to talk to you, my friend ¯\\\_(°^°)\\_/¯")
			await asyncio.sleep(2)
			await message.delete()
		# else:
	else:
		if message.content[0:22] == f"<@!{client.user.id}>":
			if message.content[23:] == "guilds":
				await message.delete()
				guilds = ""
				for guild in client.guilds:
					guilds = "\n".join([guilds,guild.name])
				await message.author.send(f"Currently i'm in {len(client.guilds)}, which are ```\n{guilds}\n```")
			else:
				await message.delete()
				logger.info(f"Bot was pinged in {message.guild.id}, by {message.author.id}")
				await message.channel.send(f'Current prefix is "{get_prefix(None,message)}"')
		else:
			await client.process_commands(message)

####################################
#error catch area
@client.event
async def on_command_error(ctx, error): 
	#checks to see if command is missing args, then sends message
	if isinstance(error, commands.MissingRequiredArgument):
		logger.info(f"{ctx.author} haven't filled all arguments.")
		await ctx.send('Please fill all required arguments! :eyes:')
		return

	#checks to see if permissions all exist
	if isinstance(error, commands.MissingPermissions):
		logger.error(f"{ctx.author.name} (ID {ctx.author.id}) tried running command they don't have permission to.")
		await ctx.send("You're missing required permissions! :x:")
		print("Someone tried to run a command that they don't have permissions for!")
		return
	
	#checks to see if command args being passed in are invalid/unparseable, then sends message
	if isinstance(error, commands.BadArgument):
		logger.info(f"{ctx.author} passed invalid arguments in arguments.")
		await ctx.send(f'Please check the arguments you provided\n{error.args[1]}')
		await ctx.send("One of them couldn't be converted to {}".format(error.args[0].split('"')[1]))
		return


	if isinstance(error, commands.BotMissingPermissions):
		logger.critical("Bot is missing required permissions.")
		await ctx.send("I'm missing administrator permissions! :x:")
		return

	if isinstance(error, commands.CommandNotFound):
		logger.info(f'{ctx.message.author.name} (ID: {ctx.message.author.id}) tried to run command "{ctx.message.content[len(get_prefix(None,ctx.message)):].split()[0]}" which does not exist.')
		await ctx.send(f'Command "{ctx.message.content[len(get_prefix(None,ctx.message)):].split()[0]}" does not exist! :x:')
		return

	logger.error(f"Unexpected error occured in command \"{ctx.command.name}\" with parameters {ctx.message.content.split()[1:]}.")
	logger.error(error.original)
	await ctx.send("An unexpected error occured! :x:")
#-----------------------------------
#Cogs Load
@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')

#Cogs Unload
@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')

for filename in os.listdir(f'{rundir}/cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

if home == '/home/tent':
	client.run(config['menotbot_token'])
else:
	client.run(config['omena_token'])
