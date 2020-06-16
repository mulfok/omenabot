import discord 
import os
import random
import pathlib
import json
import youtube_dl
import asyncio
import time
import logging
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle

lq=True

#grabs server prefix from each server
def get_prefix(client, message):
	if not prefixes[str(message.guild.id)]['prefix']:
		return '~'
	return prefixes[str(message.guild.id)]['prefix']

#Set bot command prefix!
client = commands.Bot(command_prefix = get_prefix)

client.remove_command('help')
status = cycle(['help - Brings up commands', 'aboutme - Shows bot info', 'trivia - Fun facts!', 'changeprefix - Customise server prefix!'])

rundir = pathlib.Path(__file__,).parent.absolute()
home = os.getenv('HOME')

now = time.gmtime()
start_time = f'{now[0]}_{now[1]}_{now[2]}_{now[3]}_{now[4]}_{now[5]}'
print(f"\nStarted at {start_time}")
logging.basicConfig(filename=f'{rundir}/logs/latest.log', level=logging.INFO)

with open(f'{rundir}/private/prefixes.json', 'r') as f:
	prefixes = json.load(f)

config = {}

with open(f'{rundir}/private/bot.json') as file:
	config = json.load(file)

responses = {}
with open(f"{rundir}/responselists.json") as file:
	responses = json.load(file)

#Various debug console message events
@client.event
async def on_connect():
	logging.atexit.register(close_logger)
	logging.info('Connected to discord...')

@client.event
async def on_disconnect():
	logging.info('Disconnected from discord.')
	logging.shutdown()

def close_logger():
	os.rename(f'{rundir}/logs/latest.log',f'{rundir}/logs/{start_time}.log')

@client.event
async def on_ready():
	#set status, change activity and print ready and start loop
	change_status.start()
	hail_theOwner.start()
	await client.change_presence(status=discord.Status.online, activity=discord.Game('~helpme for commands!'))
	logging.info('Ready!')
	logging.info(f'Logged in as {client.user.name}')
	logging.info(f'Client ID: {client.user.id}')
	logging.info('---------')

#Set default command prefix on server join
@client.event
async def on_guild_join(guild):
	with open(f'{rundir}/private/prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes[str(ctx.guild.id)]['prefix'] = prefix
	prefixes[str(ctx.guild.id)]['name'] = str(ctx.guild.name)

	with open(f'{rundir}/private/prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

#Purge command prefix upon server leave
@client.event
async def on_guild_remove(guild):
	with open(f'{rundir}/private/prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes.pop(str(guild.id))

	with open(f'{rundir}/private/prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

@client.command(aliases=["setprefix"])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
	with open(f'{rundir}/private/prefixes.json', 'r') as f:
		prefixes = json.load(f)

	logging.info(f'Prefix changed to {prefix} for server {ctx.guild.name} (ID {ctx.guild.id})')
	prefixes[str(ctx.guild.id)]['prefix'] = prefix
	prefixes[str(ctx.guild.id)]['name'] = str(ctx.guild.name)
	await ctx.send(f'Prefix changed to `{prefix}`! :white_check_mark:')

	with open(f'{rundir}/private/prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

@client.event
async def on_member_join(member):
	print(f'{member} has joined a server!')

@client.event
async def on_member_remove(member):
	print(f'{member} has left a server. :(')

#Tasks Area
@tasks.loop(seconds=5)
async def change_status():
	await client.change_presence(activity=discord.Game(next(status)))

@tasks.loop(seconds=10)
async def hail_theOwner():
	for guild in client.guilds:
		if random.randint(0, 99) == 0:
			await guild.text_channels[random.randint(0,len(guild.text_channels)-1)].send(f"Hail the great {guild.owner.name}, owner of this discord!")

#Commands area
@client.command()
async def ping(ctx):
	#simply reply with 'Pong!' and milliseconds
	await ctx.send(f'Pong! {round(client.latency*1000)}ms')

@client.command()
async def pingtrue(ctx):
	#reply with "pong!" and DON'T round ms
	await ctx.send(f'Pong! {client.latency*1000}ms')

#the F command
@client.command()
async def f(ctx):
	#send image link
	fresponses=["https://cdn.discordapp.com/attachments/720598695191511110/720861011032408064/F.png",
			    "https://cdn.discordapp.com/attachments/720598695191511110/721123893716189224/tenor.gif"
			   ]

	fauthor = ctx.message.author

	fembed = discord.Embed(
		colour = discord.Colour.red()
	)
	fembed.set_author(name="Paying respects...")
	fembed.set_image(url=f"{random.choice(fresponses)}")

	await ctx.send(embed=fembed)

#Random Anime Song Command
@client.command()
async def randomanimesong(ctx):
	animeresponses=["https://www.youtube.com/watch?v=AYA8DRG8cFs",
				    "https://www.youtube.com/watch?v=a78ijoi0G8s",
					"https://www.youtube.com/watch?v=z1PWA11Ec3E",
					"https://www.youtube.com/watch?v=79d4RHbNjOQ `MulfoK: Okay lol this one is reaallly bad`",
					"https://www.youtube.com/watch?v=JBqxVX_LXvk",
					"https://www.youtube.com/watch?v=lOfZLb33uCg `MulfoK: Totally an anime song`",
					"https://www.youtube.com/watch?v=m2eXg19DjPw"
				   ]
	await ctx.send(f"The developers are not weebs I swear :eyes:\n{random.choice(animeresponses)}")

@client.command(aliases=['8ball', 'eightball'])
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
	helpembed.add_field(name="mcmd0-3", value="Pulls up complete Minecraft 1.15.2 command documentation.", inline=False)
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
async def mcmd0(ctx):
	mcauthor = ctx.message.author

	mcmdembed = discord.Embed(
		colour = discord.Colour.red()
	)
	mcmdembed.set_author(name="1.15.2 Full Command Documentation Page 0")
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

	await ctx.send(embed=mcmdembed)

@client.command()
async def mcmd1(ctx):
	mcauthor1 = ctx.message.author

	mcmdembed1 = discord.Embed(
		colour = discord.Colour.red()
	)
	mcmdembed1.set_author(name="1.15.2 Full Command Documentation Page 1")
	mcmdembed1.add_field(name="/give <player> <item>[<NBT>] [<count>]", value="Gives an item to a player.", inline=False)
	mcmdembed1.add_field(name="/help [<command>]", value="Provides help for commmands.", inline=False)
	mcmdembed1.add_field(name="/kick <player> [reason]", value="Kicks a player off a server", inline=False)
	mcmdembed1.add_field(name="/kill [<targets>]", value="Kills entities.", inline=False)
	mcmdembed1.add_field(name="/list [uuids]", value="Lists players on the server.", inline=False)
	mcmdembed1.add_field(name="/locate <StructureType>", value="Locates the closest structure.", inline=False)
	mcmdembed1.add_field(name="/loot <target> <source>", value="Drops itesm from an inventory slot onto the ground.", inline=False)
	mcmdembed1.add_field(name="/me <action>", value="Displays a message about the sender.", inline=False)
	mcmdembed1.add_field(name="/tell or /msg or /w <player> <message>", value="Displays a private message to other players.", inline=False)
	mcmdembed1.add_field(name="/op <player>", value="Grants operator status to a player.", inline=False)
	mcmdembed1.add_field(name="/pardon <player>", value="Removes entries from the banlist.", inline=False)
	mcmdembed1.add_field(name="/pardon-ip <address>", value="Removes entries from the banlist.", inline=False)
	mcmdembed1.add_field(name="/particle <name> [<pos>] [<delta>] <speed> <count> [<mode>] [<viewers>]", value="Creates particles.", inline=False)
	mcmdembed1.add_field(name="/playsound <sound> <source> <player> [x] [y] [z] [volume] [pitch] [minimumVolume]", value="Plays a sound.", inline=False)
	mcmdembed1.add_field(name="/publish [port]", value="Opens single-player world to local network.", inline=False)
	mcmdembed1.add_field(name="/recipe <give|take> [player] <name|*>", value="Gives or takes player recipes.", inline=False)
	mcmdembed1.add_field(name="/reload", value="Reloads loot tables, advancements, and functions from disk.", inline=False)
	mcmdembed1.add_field(name="/replaceitem block <x> <y> <z> <slot> <item> [amount]", value="Replaces items in inventories.", inline=False)
	mcmdembed1.add_field(name="/replaceitem entity <selector> <slot> <item> [amount]", value="Replaces items in inventories.", inline=False)
	mcmdembed1.add_field(name="/save-all [flush]", value="Saves the server to disk.", inline=False)
	mcmdembed1.add_field(name="/save-off", value="Disables automatic server saves.", inline=False)
	mcmdembed1.add_field(name="/save-on", value="Enables automatic server saves.", inline=False)
	mcmdembed1.add_field(name="/say <message>", value="Displays a message to multiple players.", inline=False)
	mcmdembed1.add_field(name="/schedule function <function> <time> [append|replace]", value="Delays the execution of a function.", inline=False)
	mcmdembed1.add_field(name="/schedule clear <function>", value="Clears a scheduled function.", inline=False)

	await ctx.send(embed=mcmdembed1)

@client.command()
async def mcmd2(ctx):
	mcauthor2 = ctx.message.author

	mcmdembed2 = discord.Embed(
		colour = discord.Colour.red()
	)
	mcmdembed2.set_author(name="1.15.2 Full Command Documentation Page 2")
	mcmdembed2.add_field(name="/seed", value="Displays the world seed.", inline=False)
	mcmdembed2.add_field(name="/setblock", value="Changes a block to another block. [See official documentation](/schedule clear <function>)", inline=False)
	mcmdembed2.add_field(name="/setidletimeout <minutes until kick>", value="Sets the time before idle players are kicked.", inline=False)
	mcmdembed2.add_field(name="/setworldspawn [<x> <y> <z>]", value="Sets the world spawn.", inline=False)
	mcmdembed2.add_field(name="/spawnpoint [<player>] [<x> <y> <z>]", value="Sets the spawn point for a player.", inline=False)
	mcmdembed2.add_field(name="/spectate [target] [player]", value="Make one player in spectator mode spectate an entity.", inline=False)
	mcmdembed2.add_field(name="/spreadplayers <x> <z> <spreadDistance> <maxRange> <respectTeams> <player>", value="Teleoprts entities to random locations.", inline=False)
	mcmdembed2.add_field(name="/stop", value="Stops a server.", inline=False)
	mcmdembed2.add_field(name="/stopsound <player> [<source>] [<sound>]", value="Stops a sound.", inline=False)
	mcmdembed2.add_field(name="/summon <entity_name> [<pos>] [<nbt>]", value="Summons an entity.", inline=False)
	mcmdembed2.add_field(name="/tag <targets> add <name>", value="Adds an entity tag.", inline=False)
	mcmdembed2.add_field(name="/tag <targets> remove <name>", value="Removes an entity tag.", inline=False)
	mcmdembed2.add_field(name="/tag <targets> list", value="Lists all entity tags.", inline=False)
	mcmdembed2.add_field(name="/team", value="Controls teams. [See official documentation](/tag <targets> list)", inline=False)
	mcmdembed2.add_field(name="/teammsg <message>", value="Specifies the message to send to the team.", inline=False)
	mcmdembed2.add_field(name="/tp or /teleport", value="Teleports entities. [See offical documentation](https://minecraft.gamepedia.com/Commands/tp)", inline=False)
	mcmdembed2.add_field(name="/tellraw <player> <raw json message>", value="Displays a JSON message to players.", inline=False)
	mcmdembed2.add_field(name="/time <add|query|set> <value>", value="Changes or queries the world's game time.", inline=False)
	mcmdembed2.add_field(name="/title", value="Manages screen titles. [See offical documentation](https://minecraft.gamepedia.com/Commands/title)", inline=False)
	mcmdembed2.add_field(name="/trigger <objective> [<add|set> <value>]", value="Sets a trigger to be activated.", inline=False)
	mcmdembed2.add_field(name="/weather <clear|rain|thunder> [duration]", value="Sets the weather.", inline=False)
	mcmdembed2.add_field(name="/whitelist add <player>", value="Adds a player to whitelist.", inline=False)
	mcmdembed2.add_field(name="/whitelist remove <player>", value="Removes a player from whitelist.", inline=False)
	mcmdembed2.add_field(name="/whitelist [on|off|list|reload]", value="Manages server whitelist.", inline=False)
	mcmdembed2.add_field(name="/worldborder", value="Manages the world border. [See official documentation](/worldborder)", inline=False)
	mcmdembed3.add_field(name="/xp [add|set] <players> <amount> [points|levels]", value="Adds or removes player experience.", inline=False)
	mcmdembed3.add_field(name="/xp query <player> <amount> [points|levels]", value="Displays a player's current experience.", inline=False)

	await ctx.send(embed=mcmdembed2)

@client.command()
async def mcmd3(ctx):
	mcauthor3 = ctx.message.author

	mcmdembed3 = discord.Embed(
		colour = discord.Colour.red()
	)
	mcmdembed3.set_author(name="1.15.2 Full Command Documentation Page 3")
	mcmdembed3.add_field(name="/xp [add|set] <players> <amount> [points|levels]", value="Adds or removes player experience.", inline=False)
	mcmdembed3.add_field(name="/xp query <player> <amount> [points|levels]", value="Displays a player's current experience.", inline=False)

	await ctx.send(embed=mcmdembed3)

@client.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount : int):
	if amount < 0:
		await ctx.send("That's not a valid arguement! :negative_squared_cross_mark:")
		time.sleep(1)
		await ctx.channel.purge(limit=2)
	elif amount > 100:
		await ctx.send("Purge limit is 100! :negative_squared_cross_mark:")
		time.sleep(1)
		await ctx.channel.purge(limit=2)
	else:
		await ctx.channel.purge(limit=amount + 1)
		time.sleep(0.1)
		message = await ctx.send(f"Removed {amount} messages.")
		time.sleep(3.3)
		await message.delete()

@client.command()
async def aboutme(ctx):
	await ctx.send("```\nOmena!BOT a4.0.5\n" + \
				   "Developed by:\n" + \
				   "MulfoK: Lead Programmer\n" + \
				   "lenrik1589: Programmer\n" + \
				   "Brady: Music Programmer(?)\n" + \
				   "General Purpose Discord Bot\n" + \
				   "Written in Python 3.8.2\n" + \
				   "help for commands list (~ is default prefix)```")

@client.command()
@commands.has_permissions(administrator=True)
#set params and kick
async def kick(ctx, member: discord.Member, *, reason=None):
	logging.critical(f'{member.mention} (ID {member.id}) was kicked from server {ctx.guild.id} with reason: "{reason}".')
	await member.kick(reason=reason)
	await ctx.send(f'{member.mention} was kicked from the server. :hammer:')

@client.command()
@commands.has_permissions(administrator=True)
#set params and BAN
async def ban(ctx, member : discord.Member, *, reason=None):
	logging.critical(f'{member.mention} (ID {member.id}) was banned from server {ctx.guild.id} with reason: "{reason}".')
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
			logging.critical(f'{member.mention} (ID {member.id}) was unbanned from server {ctx.guild.id}.')
			await ctx.guild.unban(user)
			await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
			return

#Developer Commands
##################################################################
#stops bot command
@client.command(aliases=["quit", "exit", "stop"])
async def close(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 465816879072542720 or attempt_id == 437296242817761292: #first id is mulfok, second is lenrik
		await ctx.send("Shutting down... See ya! :lock:")
		time.sleep(0.5)
		await ctx.channel.purge(limit=2)
		logging.info(f'Bot Closed By {ctx.author.name} ID: {ctx.author.id}')
		await client.close()
		print(f'Bot Closed By {ctx.author.name} ID: {ctx.author.id}')

	else:
		logging.info(f"{ctx.author} (ID:{ctx.author.id}) tried to close the bot!")
		await ctx.send("You're not a developer! :x:")
		print(f"{ctx.author} (ID:{ctx.author.id}) tried to close the bot!")

#github link command (useful for if you lost the link or something)
@client.command()
async def github(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 437296242817761292 or attempt_id == 465816879072542720 or attempt_id == 691668587005607957 or attempt_id == 634189650608652310: #first id is lenrik, second is mulfok, third is wullie, fourth is brady
		await ctx.author.send("Github (Private): https://github.com/MulfoK/omenabot1.0\nShh... Let's not leak our hard work!")
		await ctx.send("You have been private messaged the github link. :white_check_mark:")
		logging.info(f"Github pulled up by {ctx.author} ID: {ctx.author.id}")
		time.sleep(1)
		await ctx.channel.purge(limit=2)

	else:
		await ctx.send("You're not a developer! :x:")
		logging.info(f"{ctx.author} (ID {ctx.author.id}) tried to pull up github link!")

#todo command
@client.command()
async def todo(ctx):
	attempt_id = ctx.author.id
	if attempt_id == 437296242817761292 or attempt_id == 465816879072542720 or attempt_id == 691668587005607957 or attempt_id == 634189650608652310: #first id is mulfok, second is lenrik, third is wullie, fourth is brady
		await ctx.author.send("I feel sorry for you developers...\n" + \
							  "```Our epic todo list:\n" + \
							  "1: Integrate a music player into Omena\n" + \
							  "2: Get a ~calc command working\n```"
							 )
		await ctx.send("The developer to-do list has been private messaged to you! :white_check_mark:")
		logging.info(f"Todo list pulled up by {ctx.author} ID: {ctx.author.id}")

	else:
		await ctx.send("You're not a developer! :x:")
		logging.info(f"{ctx.author} (ID {ctx.author.id}) tried to pull of the developer to-do list!")
#######################################################
# musi

#join command
@client.command()
async def join(ctx):
	voice = ctx.author.voice
	if not voice == None:
		await ctx.send(f'Connecting to {voice.channel.name}')
		await voice.channel.connect()
	else:
		await ctx.send('Make sure to be connectaed to voice chat on this server.')

#disconnect command
@client.command()
async def disconnect(ctx):
	voice = ctx.author.voice
	if not voice == None:
		await ctx.send(f'Disconnecting from {voice.channel.name}')
		await ctx.voice_client.disconnect()
	else:
		await ctx.send('Make sure to be connectaed to voice chat on this server.')

# play?
@client.command(aliases=["p"])
async def play(ctx):
	song = f'{rundir}/private/song.mp3'
	if not ctx.voice_client == None:
		source = discord.FFmpegOpusAudio(song)
		await ctx.send(f'Playing: "{song}".')
		await ctx.voice_client.play(source, after=looped)
	else:
		await ctx.send("Not connected to any voice chat.")

# looped play
async def looped(err):
	print(err)
	if lq:
		await play()

#######################################################
#calc command
@client.command()
async def calc(ctx):
	result='calc command is not done yet. :P'
	joint = ctx.message.content[len(get_prefix('',ctx)) + 4:].replace(' ', '')
	if not joint.isascii():
		await ctx.send(f"{get_prefix('',ctx)}calc only accepts ASCII characters as input!")
		return
	elif len(joint.replace(["+", "-", "/", '\\',' % ',' ^ ',' * '],' ')) < 1:
		await ctx.send(f'You should add atleast one digit to have calculation possible.')
		return
	await ctx.send(result)

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
@client.command(aliases=["if"])
async def _if(ctx):
	if ctx.author.id == 465816879072542720:
		await ctx.send("Go learn if statments you madman. :dagger:")

	else:
		await ctx.send("This command isn't for you! :x:")

#hack command
@client.command()
async def hack(ctx, *, hackvic):
	message = ctx.message
	#store homework amount in temp variable
	homeworkstorage = random.choice(responses["hack"]["homework"])
	#send messages in a timely order
	hack_message = await ctx.send(f"Hacking {hackvic}...")
	time.sleep(2)
	await message.delete()
	await hack_message.edit(content=f"Grabbing {homeworkstorage} 'Homework' folder...")
	time.sleep(2)
	await hack_message.edit(content=f'Selling data to {random.choice(responses["hack"]["companies"])}...')
	time.sleep(2)
	await hack_message.edit(content=f"Laughing evilly...")
	time.sleep(2)
	await hack_message.edit(content="Bypassing Discord security...")
	time.sleep(2)
	mail_before, mail_after = random.choice(responses['hack']['mail_body'])
	await hack_message.edit(content=f"Email: {mail_before}{hackvic}{mail_after}@{random.choice(responses['hack']['mail_provider'])}\nPassword: ihateyouihateyougodie")
	time.sleep(2)
	await hack_message.edit(content=f"Reporting {hackvic} for breaking Discord TOS...")
	time.sleep(2)
	await hack_message.edit(content=f"Payment recieved: {random.choice(responses['hack']['payment'])}")
	time.sleep(1)
	await hack_message.edit(content=f"Laughing evilly...")
	await hack_message.delete()
	await ctx.send(f"The 100% real hack is complete.")
	await ctx.send(f"Homework folder size: {homeworkstorage}")

@client.command()
async def slap(ctx, *, arg):
	await ctx.send(f"Slapped {arg}!")

#joke command
@client.command()
async def joke(ctx):
	
	joke, punchline = random.choice(responses["jokes"])
	await ctx.send(joke)
	time.sleep(2)
	await ctx.send(punchline)

#-----------------------------------
#error catch area
@client.event
async def on_command_error(ctx, error): 
	#checks to see if command is missing args, then sends message
	if isinstance(error, commands.MissingRequiredArgument):
		logging.info(f"{ctx.author} haven't filled all arguments.")
		await ctx.send('Please fill all required arguments! :eyes:')
		return

	#checks to see if permissions all exist
	if isinstance(error, commands.MissingPermissions):
		logging.error(f"{ctx.author.name} (ID {ctx.author.id}) tried running command they don't have permission to.")
		await ctx.send("You're missing required permissions! :x:")
		print("Someone tried to run a command that they don't have permissions for!")
		return

	if isinstance(error, commands.BotMissingPermissions):
		logging.critical("Bot is missing required permissions.")
		await ctx.send("I'm missing administrator permissions! :x:")
		return
#-----------------------------------
#Cogs Load
@client.command()
async def load(ctx, extension):
	client.load_extension(f'cogs.{extension}');

#Cogs Unload
@client.command()
async def unload(ctx, extension):
	client.unload_extension(f'cogs.{extension}');

for filename in os.listdir(f'{rundir}/cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

if home == '/home/tent':
	client.run(config['menotbot_token'])
else:
	client.run(config['omena_token'])