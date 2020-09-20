import discord 
import os
import re
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
from math import sin, cos, tan, sqrt, asin, acos, atan, ceil, floor, pow, degrees as deg, radians as rad
from discord.ext import commands, tasks
from colorama import Fore, Back, Style, init as iniTerminaltStyling
import inspect
from discord.utils import get
from itertools import cycle

### List comprehesions: wanted_roles = [i[7:] for i in message.content.split("\n")]
### Lambdas: wanted_roles = list(map(lambda i: i[7:], message.content.split("\n")))

iniTerminaltStyling(autoreset=True)

lq = True
stop_pings = False

rundir = pathlib.Path(__file__,).parent.absolute()
home = os.getenv('HOME')

now = time.gmtime()
start_time = f'{now[0]}_{now[1]}_{now[2]}_{now[3]}_{now[4]}_{now[5]}'
try:
	os.remove(f'{rundir}/logs/latest.log')
except FileNotFoundError:
	print("{Style.DIM}No latest log.")
finally:
	open(f'{rundir}/logs/{start_time}.log','x')
os.symlink(f'{rundir}/logs/{start_time}.log',f'{rundir}/logs/latest.log')

print(f"Started at {Style.BRIGHT}{Fore.YELLOW}{start_time}")
logging.basicConfig(filename=f'{rundir}/logs/latest.log', level=logging.INFO)
logger = logging.getLogger("bot.main")
logger.info(f'Started at {start_time}.')

servers = {}
with open(f'{rundir}/private/servers.json') as f:
	servers = json.load(f)

dnd_conf = {}
with open(f'{rundir}/private/dnd.json') as f:
	dnd_conf = json.load(f)

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

# client.remove_command('help')
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
	print(f"{Fore.GREEN}Ready")

@client.command(name='dummy_log', help="Creates a dummy log of all types and prints message into console.\nCan only be used by developer.", brief="Test if logging works.", hidden=True)
async def dummy_log(ctx: discord.ext.commands.Context):
	attempt_id = ctx.author.id
	if attempt_id == 465816879072542720 or attempt_id == 437296242817761292: #first id is mulfok, second is lenrik
		logger.debug("dummy debug log message")
		logger.info("dummy info log message")
		logger.warning("dummy warning log message")
		logger.error("dummy error log message")
		logger.critical("dummy critical log message")
		newLine = "\n"
		newLineCitation = "\n> "
		messageToLog = ctx.message.content.replace(newLine,newLineCitation)
		logger.info(f"actual message: {messageToLog}")
		print("{Fore.YELLOW}dummy message terminal")
		print("{Fore.GREEN}another message but\nspilt\ninto lines.")
		message = await ctx.send("debug log created")
		await asyncio.sleep(1)
		await message.delete()
	await ctx.message.delete()

#Set default command prefix on server join
@client.event
async def on_guild_join(guild):
	global servers
	logger.info(f'Bot joined {guild.name} (ID: {guild.id})')
	print(f'{Fore.MAGENTA}Bot has joined {guild.name} (ID: {guild.id})!')
	with open(f'{rundir}/private/servers.json', 'r') as f:
		servers = json.load(f)

	servers[str(guild.id)] = {}
	servers[str(guild.id)]["prefix"] = '~'

	with open(f'{rundir}/private/servers.json', 'w') as f:
		json.dump(servers, f, indent=2)

#Purge command prefix upon server leave
@client.event
async def on_guild_remove(guild):
	global servers
	logger.info(f'Bot left {guild.name} (ID: {guild.id})')
	with open(f'{rundir}/private/servers.json', 'r') as f:
		servers = json.load(f)

	servers.pop(str(guild.id))

	with open(f'{rundir}/private/servers.json', 'w') as f:
		json.dump(servers, f, indent=2)

@client.command(aliases=["setprefix"],help="Sets command prefix.\nOnly admins can use it.",brief="Sets command prefix.",hidden=False)
async def changeprefix(ctx: discord.ext.commands.Context, prefix):
	global servers
	if ctx.author.guild_permissions.administrator or not config['devs'].get(f'{ctx.author.id}' == None):
		with open(f'{rundir}/private/servers.json', 'r') as f:
			servers = json.load(f)

		logger.info(f'Prefix changed to {prefix} for server {ctx.guild.name} (ID {ctx.guild.id})')
		servers[str(ctx.guild.id)]['prefix'] = prefix
		servers[str(ctx.guild.id)]['name'] = str(ctx.guild.name)
		await ctx.send(f'Prefix changed to `{prefix}`! :white_check_mark:')

		with open(f'{rundir}/private/servers.json', 'w') as f:
			json.dump(servers, f, indent=2)
	else:
		commands.MissingPermissions(ctx.author.guild_permissions.administrator)

@client.command(name="set",brief="Configuration command.",hidden=False)
async def setParam(ctx: discord.ext.commands.Context, param: str, *value: str):
	global servers
	"""Command for configuring different bot parameters for current  guild.
	"""
	try:
		if (param == "permanick"):
			if not ctx.author.guild_permissions.manage_nicknames and not ctx.author.guild_permissions.administrator and config["devs"].get(f"{ctx.author.id}") == None:
				raise commands.MissingPermissions(discord.permissions.Permissions(permissions=1 << 27))
			member = {}
			if len(ctx.message.mentions) == 1:
				member = ctx.message.mentions[0]
			elif len(value[0]) == len("564489099512381440"):
				member = ctx.guild.get_member(int(value[0]))
			else:
				member = ctx.guild.get_member(int(value[0][2:-1]))
			await ctx.message.delete()
			if servers[f'{ctx.guild.id}'].get("nicks") == None:
				servers[f'{ctx.guild.id}']["nicks"] = {}
			if len(value) < 2:
				if not servers[f'{ctx.guild.id}']["nicks"].get(f'{member.id}') == None:
					servers[f'{ctx.guild.id}']["nicks"].pop(f'{member.id}')
					message = await ctx.send(f"reset permanent nick for {member}")
					await member.edit(nick = None)
					await asyncio.sleep(3)
					await message.delete()
			else:
				permanentnick = ' '.join(value[1:])
				if len(permanentnick) > 32:
					message = await ctx.send(f"Nickname \`{permanentnick}\` is too long (32 characters max).")
					await asyncio.sleep(7)
					await message.delete()
					return
				servers[f'{ctx.guild.id}']["nicks"][f'{member.id}'] = permanentnick
				message = await ctx.send(f"permanent nick for {member} is now set to \`{permanentnick}\`")
				await member.edit(reason="no reason, lol", nick = permanentnick)
				await asyncio.sleep(3)
				await message.delete()
			with open(f'{rundir}/private/servers.json', 'w') as f:
				json.dump(servers, f, indent=2)
			return
		elif (param == "channel"):
			if ctx.author.guild_permissions.manage_channels or not config["devs"].get(f"{ctx.author.id}") == None:
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
						await message.delete()
						await ctx.message.delete()
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
						print(f'not setting chat {value[0]} to anywhere as invalid parameters are passed in.')
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
	except discord.errors.Forbidden:
		with open(f'{rundir}/private/servers.json', 'w') as f:
			json.dump(servers, f, indent=2)

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
async def on_member_join(member: discord.Member):
	if servers[f'{member.guild.id}'].get('name') == None:
		servers[f'{member.guild.id}']['name'] = member.guild.name
	if member.guild.id == 663903542842490910:
		print(f"{Fore.MAGENTA}{member} joined testman")
	logger.info(f'{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')
	print(f'{Fore.GREEN}{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')

@client.event
async def on_member_update(member_before: discord.Member, member_after: discord.Member):
	if not member_before.nick == member_after.nick:
		if not servers.get(f'{member_after.guild.id}') == None:
			if not servers[f'{member_after.guild.id}'].get("nicks") == None:
				if not servers[f'{member_after.guild.id}']["nicks"].get(f'{member_after.id}') == None:
					if not servers[f'{member_after.guild.id}']["nicks"][f'{member_after.id}'] == member_after.nick:
						await member_after.edit(reason="permanent nickname", nick=servers[f'{member_after.guild.id}']["nicks"][f'{member_after.id}'])

@client.event
async def on_member_remove(member: discord.Member):
	if servers[f'{member.guild.id}'].get('name') == None:
		servers[f'{member.guild.id}']['name'] = member.guild.name
	if member.guild.id == 663903542842490910:
		print(f"{Fore.MAGENTA}{member} left testman")
		print(member.guild.system_channel())
	logger.info(f'{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')
	print(f'{Fore.RED}{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')

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

@client.command()
async def pong(ctx: commands.context):
	await ctx.send("ping, :ping_pong:!")

#Commands area
@client.command()
async def ping(ctx: commands.context, *varg):
	if varg == ():
		#simply reply with 'Pong!' and milliseconds
		await ctx.send(f'Pong! {round(client.latency*1000)}ms')
	else:
		pings = 1
		delay = 1
		if len(varg) > 1:
			pings = int(varg[1])
			pings = min(pings, 100)
			if len(varg) > 2:
				delay = float(varg[2])
				delay = max(delay, 1)
		varg = varg[0]
		userId = int(varg[3:-1])
		user = ctx.guild.get_member(userId)
		enabled = config['ping'][str(userId)]
		if enabled == None:
			enabled = False
		if enabled:
			initial_pings = pings
			logger.warning(f"{ctx.author.name} (ID: {ctx.author.id}) requested to ping {user.name} {pings} times with delay of {delay} seconds.")
			while pings > 0:
				pings -= 1
				if stop_pings:
					pings = 0
					await ctx.send(f"<@{user.id}>, pings were stopped.")
				elif pings > 0:
					await ctx.send(f"<@{user.id}>, ping № {initial_pings-pings} out of {initial_pings} (ETA:{parse_duration(int(delay*pings))})")
				else:
					await ctx.send(f"<@{user.id}>, ping № {initial_pings-pings}. **last ping**.")
				await asyncio.sleep(delay)
		else:
			await ctx.send(f"Pinging `{user.name}` is not enabled but they can enable it if they want.")

@client.command(name="toggle")
async def toggle(ctx: discord.ext.commands.Context, command: str, *varg: str):
	global config
	if command == "ping":
		if not isinstance(varg, str):
			varg = ''
		user = ''
		if not ctx.message.mentions == []:
			user = ctx.message.mentions[0]#int(varg[3:-1]))
		else:
			user = ctx.author
		enabled = config['ping'].get(f'{user.id}')
		if enabled == None:
			enabled = False
		if ctx.author == user or ctx.author.guild_permissions.manage_messages:
			config['ping'][f'{user.id}'] = not enabled
			with open(f'{rundir}/private/bot.json', 'w') as file:
				json.dump(config, file, indent=2)
			response = None
			if enabled:
				response = await ctx.send(f"Pings successfully toggled for {user.name} (now disabled)")
			else:
				response = await ctx.send(f"Pings successfully toggled for {user.name} (now enabled)")
			await asyncio.sleep(3)
			await response.delete()
		else:
			response = await ctx.send(f"That's not how it works, you can't decide whether you can annoy {user.name} just because, only {user.name} can :P")
			await asyncio.sleep(3)
			await response.delete()

@client.command()
async def pingtrue(ctx):
	#reply with "pong!" and DON'T round ms
	await ctx.send(f'Pong! {client.latency*1000}ms')

#the F command
@client.command(name = "f")
async def f_command(ctx):
	#send image link

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
	await ctx.message.delete()
	await ctx.send(f'Question: "`{question}``" by {ctx.author.name}\nAnswer: {random.choice(responses["8ball"])}')

@client.command()
async def trivia(ctx):
	#output random answer
	await ctx.send(f'{random.choice(responses["trivia"])}')

@client.command(brief="minecraft 1.15.2 commands")
async def mcmd(ctx: discord.ext.commands.Context, *, page:int=1):
	"""
	"""

	mcmdembed = discord.Embed(
		colour=discord.Colour.red(),
		author='1.15.2 Full Command Documentation Page' 
	)
	if page <= len(responses['mc_commands']) and page > 0:
		mcmdembed.set_author(name=f"1.15.2 Full Command Documentation Page {page}/{len(responses['mc_commands'])}")
		mcmdembed.set_footer(text=f"1.15.2 Full Command Documentation Page {page}/{len(responses['mc_commands'])}")
		for command in responses['mc_commands'][page - 1]:
			mcmdembed.add_field(name=command, value = responses['mc_commands'][page - 1][command], inline=False)
	else:
		await ctx.send(f"Sorry, there's no page №{page}")
		return

	await ctx.send(embed=mcmdembed)

@client.command()
async def clear(ctx: discord.ext.commands.Context, amount: int):
	perms = ctx.message.author.permissions_in(ctx.channel)
	if perms.manage_messages or not config["devs"].get(f"{ctx.author.id}") == None:
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
		commands.MissingPermissions(perms.manage_messages)

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
	if perms.administrator or not config["devs"].get(f"{ctx.author.id}") == None:
		logger.critical(f'{member.mention} (ID {member.id}) was kicked from server {ctx.guild.id} with reason: "{reason}".')
		await member.kick(reason=reason)
		await ctx.send(f'{member.mention} was kicked from the server. :hammer:')
	else:
		commands.MissingPermissions(perms.manage_members)

@client.command()
@commands.has_permissions(administrator=True)
#set params and BAN
async def ban(ctx, member, *, reason=None):
	perms = ctx.message.author.permissions_in(ctx.channel)
	if perms.administrator or not config["devs"].get(f"{ctx.author.id}") == None:
		member = ctx.guild.get_member(int(member[3: -1]))
		logger.critical(f'{member.mention} (ID {member.id}) was banned from server {ctx.guild.id} with reason: "{reason}".')
		await member.ban(reason=reason)
		await ctx.send(f'{member.mention} was banned from the server. :hammer:')
	else:
		commands.MissingPermissions(perms.administrator)

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
@client.command(aliases=["quit", "exit"], hidden = True)
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
@client.command(hidden = True)
async def github(ctx):
	if not config["devs"].get(f"{ctx.author.id}") == None:
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
	if not config["devs"].get(f"{ctx.author.id}") == None:
		await ctx.author.send("I feel sorry for you developers...\n" + \
							  "```Our epic todo list:\n" + \
							  "1: Make music.py atleast work"
							 )
		await ctx.send("The developer to-do list has been private messaged to you! :white_check_mark:")
		logger.info(f"Todo list pulled up by {ctx.author} ID: {ctx.author.id}")

	else:
		await ctx.send("You're not a developer! :x:")
		logger.info(f"{ctx.author} (ID: {ctx.author.id}) tried to pull of the developer to-do list!")
#######################################################
#calc command
@client.command(brief="calculate your expressions", usage="expression")
async def calc(ctx: discord.ext.commands.Context, *equation: str):
	"""
	Evaluates your expression in python.
	NOTE: spaces need to be escaped i.e. \"for i\" needs to be \"for\\ i\".

	The command currently supports these operators:
	``````c++
	sin(value) get sine of value (expects radians)
	cos(value) get cosine of value (expects radians)
	tan(value) get tangent of value (expects radians)
	sqrt(value) get square root of value
	asin(value) get arc sine of value (expects radians)
	acos(value) get arc cosine of value (expects radians)
	atan(value) get arc tangent of value (expects radians)
	ceil(value) get closest smaller integer to value
	floor(value) get closest bigger integer to value
	pow(value, pow) raise value to power 
	deg(value) convert radian value to degrees
	rad(value) convert degree value to radians
	"""

	notEscapedEquation = [re.sub(r"\\$", " ", s, 0, re.MULTILINE) for s in equation]
	print(notEscapedEquation)
	splicedEquation = " ".join(notEscapedEquation)
	variables = {
		"sin":   sin,
		"cos":   cos,
		"tan":   tan,
		"sqrt":  sqrt,
		"asin":  asin,
		"acos":  acos,
		"atan":  atan,
		"ceil":  ceil,
		"floor": floor,
		"pow":   pow,
		"deg":   deg,
		"rad":   rad
	}
	variableDeclRegEx = r"(?:(\w*)=;)"
	matches = re.finditer(variableDeclRegEx, splicedEquation, re.MULTILINE)
	splicedEquation = re.sub(variableDeclRegEx, "", splicedEquation, 0, re.MULTILINE)

	for _, match in enumerate(matches, start=1):
		variables[match.group(1)] = None

	result = 0
	try:
		result = eval(splicedEquation, variables)
	except NameError:
		await ctx.send("error evaluating your expression:\n\tuse of variables is not implemented.")
		return
	except Exception as e:
		await ctx.send("%s" %e)
		return
	print(result)
	splicedEquation = splicedEquation.replace("*","\*")
	await ctx.send(f"{splicedEquation} = {result}")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#easter egg commands
#alcohol command
@client.command(hidden=True)
async def alcohol(ctx):
	if ctx.author.id == 397573419811602442: #karnage 397573419811602442
		await ctx.seyound("Go drink alcohol you madman. :beer:")

	else:
		await ctx.send("This command isn't for you! :x:")

#coffee command
@client.command(hidden=True)
async def coffee(ctx):
	if ctx.author.id == 721045183982207046: #lenrick 721045183982207046
		await ctx.send("Go drink coffee you madman. :coffee:")

	else:
		await ctx.send("This command isn't for you! :x:")

#ifstatment command
@client.command(name="if",hidden=True)
async def _if(ctx):
	if ctx.author.id == 465816879072542720:
		await ctx.send("Go learn if statments you madman. :dagger:")

	else:
		await ctx.send("This command isn't for you! :x:")

#hack command
@client.command(hidden=True)
async def hack(ctx: discord.ext.commands.Context, *, hackvic):
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

@client.command(hidden=True)
async def slap(ctx, *, person: discord.User):
	await ctx.send(f"Slapped {person}!")

#joke command
@client.command(brief="…tells a joke.", help="Blame <@465816879072542720> for it's all his fault")
async def joke(ctx):
	joke, punchline = random.choice(responses["jokes"])
	message = await ctx.send(joke)
	await asyncio.sleep(2)
	await message.edit(content=joke+"\n"+punchline)

#-----------------------------------
# emergency command
@client.event
async def on_message(message: discord.Message):
	global servers
	if not message.author == client.user:
		if message.channel.type.name == 'private':
			if not message.author == client.user and message.content:
				await client.process_commands(message)
				message = await message.channel.send("I'm a bot, and certanly not smart enough to talk to you, my friend ¯\\\_(°^°)\\_/¯")
				await asyncio.sleep(2)
				await message.delete()
		else:
			if servers.get(f'{message.guild.id}') == None:
				servers[f'{message.guild.id}'] = {}
				servers[f'{message.guild.id}']['name'] = message.guild.name
				with open(f'{rundir}/private/servers.json', 'w') as f:
					json.dump(servers, f, indent=2)
			if servers[f'{message.guild.id}'].get("name") == None:
				servers[f'{message.guild.id}']['name'] = message.guild.name
				with open(f'{rundir}/private/servers.json', 'w') as f:
					json.dump(servers, f, indent=2)
			if not servers[f'{message.guild.id}']["name"] == message.guild.name:
				servers[f'{message.guild.id}']['name'] = message.guild.name
				with open(f'{rundir}/private/servers.json', 'w') as f:
					json.dump(servers, f, indent=2)
			channels = servers[f'{message.guild.id}'].get('channels')
			if not channels == None:
				image_only = channels.get('image_only')
				if not image_only == None:
					if message.channel.permissions_for(message.guild.get_member(client.user.id)).manage_messages:
						if message.channel.id == image_only:
							if message.attachments == []:
								await message.delete()
								return
			if not message.content.startswith(".."):
				await client.process_commands(message)
			if message.content[0:22] == f"<@!{client.user.id}>":
				if message.content[23:] == "guilds":
					await message.delete()
					guilds = ""
					for guild in client.guilds:
						guilds = "\n".join([guilds, guild.name + f' (ID: {guild.id})'])
					await message.author.send(f"Currently i'm in {len(client.guilds)}, which are ```\n{guilds}\n```")
				else:
					await message.delete()
					logger.info(f"Bot was pinged in {message.guild.id}, by {message.author.id}")
					await message.channel.send(f'Current prefix is "{get_prefix(None,message)}"')

####################################
#error catch area
@client.event
async def on_command_error(ctx, error):
	#checks to see if command is missing args, then sends message
	if isinstance(error, commands.MissingRequiredArgument):
		logger.info(f"{ctx.author} haven't filled all arguments.")
		await ctx.send('Please fill all required arguments! :eyes:')
		return

	if isinstance(error, discord.errors.Forbidden):
		await ctx.send('Bot\'s missing permissions')
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
		logger.info(f'{ctx.message.author.name} (ID: {ctx.message.author.id}) tried to run command "{ctx.invoked_with}" which does not exist.')
		await ctx.send(f'Command "{ctx.invoked_with}" does not exist! :x:')
		return

	# if isinstance(error, commands.CommandInvokeError):
	# 	logger.info(f'{ctx.message.author.name} (ID: {ctx.message.author.id}) tried to run command "{ctx.invoked_with}" with args {ctx.args[1:]}.')
	# 	await ctx.send(f'Command "{ctx.message.content[len(get_prefix(None,ctx.message)):].split()[0]}" does not exist! :x:')
	# 	return

	logger.error(f"Unexpected error occured in command \"{ctx.command.name}\" with parameters {ctx.args[1:]}.")
	logger.error(error.original)
	await ctx.send("An unexpected error occured! :x:")

#-----------------------------------
#Cogs Load
@client.command(hidden=True)
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}')

#Cogs Unload
@client.command(hidden=True)
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}')

for filename in os.listdir(f'{rundir}/cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(config['token'])
