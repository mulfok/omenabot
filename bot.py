import discord 
import os
import random
import pathlib
import json
import youtube_dl
import asyncio
from discord.ext import commands, tasks
from discord.utils import get
from itertools import cycle

#grabs server prefix from each server
def get_prefix(client, message):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	return prefixes[str(message.guild.id)]

#Set bot command prefix!
client = commands.Bot(command_prefix = get_prefix)

client.remove_command('help')
status = cycle(['help - Brings up commands', 'aboutme - Shows bot info', 'trivia - Fun facts!', 'changeprefix - Customise server prefix!'])

rundir = pathlib.Path(__file__,).parent.absolute()

config = {}

with open(f'{rundir}/bot.json') as file:
	config = json.load(file)

#Various debug console message events
@client.event
async def on_connect():
	print('Connected to discord...')

@client.event
async def on_disconnect(): 
	print('Disconnected from discord.')

@client.event
async def on_ready():
	#set status, change activity and print ready and start loop
	change_status.start()
	await client.change_presence(status=discord.Status.online, activity=discord.Game('~helpme for commands!'))
	print('Ready!')
	print(f'Logged in as {client.user.name}')
	print(f'Client ID: {client.user.id}')
	print('---------')

#Set default command prefix on server join
@client.event
async def on_guild_join(guild):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes[str(guild.id)] = '~'

	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

#Purge command prefix upon server leave
@client.event
async def on_guild_remove(guild):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes.pop(str(guild.id))

	with open('prefixes.json', 'w') as f:
		json.dump(prefixes, f, indent=4)

#music player

@client.command()
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, prefix):
	with open('prefixes.json', 'r') as f:
		prefixes = json.load(f)

	prefixes[str(ctx.guild.id)] = prefix
	await ctx.send(f'Prefix changed to `{prefix}`! :white_check_mark:')

	with open('prefixes.json', 'w') as f:
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

#Commands area
@client.command()
async def ping(ctx):
	#simply reply with 'Pong!' and milliseconds
	await ctx.send(f'Pong! {round(client.latency)}ms')

@client.command()
async def pingtrue(ctx):
	#reply with "pong!" and DON'T round ms
	await ctx.send(f'Pong! {client.latency}ms')

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
	#list of repsonses
	responses = ["It is certain.",
				 "It is decidedly so.",
				 "Without a doubt.",
				 "Yes - definitely.",
				 "You may rely on it.",
				 "As I see it, yes.",
				 "Most likely.",
				 "Outlook good.",
				 "Yes.",
				 "Signs point to yes.",
				 "Reply hazy, try again.",
				 "Ask again later.",
				 "Better not tell you now.",
				 "Cannot predict now.",
				 "Concentrate and ask again.",
				 "Don't count on it.",
				 "My reply is no.",
				 "My sources say no.",
				 "Outlook not so good.",
				 "Very doubtful."
				]
	#output random answer
	await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

@client.command()
async def trivia(ctx):
	#list of repsonses
	responsestrivia = ["Elephants can't jump!",
					   "Quokkas are a marspial!",
					   "MulfoK runs a dual boot of Kubuntu 20.04!",
					   "Omena means 'apple' in Finnish!",
					   "MulfoK is from Scotland!",
					   "Flamingos get their pink colour from eating shrimp!",
					   "Dolphins can't smell!",
					   "There are 50 states in the USA!",
					   "One Venus day is equal to 116 Earth days!",
					   "A '#' is called an octothorp!",
					   "A group of whales is called a pod!",
					   "Jack-O'-lanterns were originally made with turnips, not pumpkins!",
					   "The blue M&M was introduced in 1995!",
					   "Lenrik is not a good programmer!",
					   "Bow down to Rib!",
					   "Fingers don't have muscles!"
					  ]
	#output random answer
	await ctx.send(f'{random.choice(responsestrivia)}')

@client.command()
async def help(ctx):
	author = ctx.message.author

	helpembed = discord.Embed(
		colour = discord.Colour.red()
	)
	helpembed.set_author(name="Default Bot Prefix: ~")
	helpembed.add_field(name="help", value="Shows the command menu to you.", inline=False)
	helpembed.add_field(name="ping", value="Returns your ping in milliseconds.", inline=False)
	helpembed.add_field(name="pingtrue", value="Returns your ping in milliseconds *without* rounding.", inline=False)
	helpembed.add_field(name="8ball/eightball [question]", value="A Magic Eight Ball Simulator.", inline=False)
	helpembed.add_field(name="clear [number]", value="Clears a set amount of messages. (Requires manage messages permission)", inline=False)
	helpembed.add_field(name="aboutme", value="Shows bot info", inline="False")
	helpembed.add_field(name="kick [member]", value="Kicks a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="ban [member]", value="Bans a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="unban [member]", value="Unbans a member. (Requires admin permission)", inline=False)
	helpembed.add_field(name="close/exit/quit", value="Shuts the bot down. (Developer-Only Command)", inline=False)
	helpembed.add_field(name="minesweeper [columns] [rows] [bombs]", value="Starts up a game of spoiler-based Minesweeper. (If args left empty, game will start with random settings)", inline=False)
	helpembed.add_field(name="mcmd0-3", value="Pulls up complete Minecraft 1.15.2 command documentation.", inline=False)
	helpembed.add_field(name="trivia", value="Random facts about the developer and interesting things!", inline=False)
	helpembed.add_field(name="slap [person]", value="Slap whoever you choose!", inline=False)
	helpembed.add_field(name="changeprefix [prefix]", value="Changes server prefix. (Requires admin permission)", inline=False)
	helpembed.add_field(name="f", value="Sends a random image of the letter F.", inline=False)
	helpembed.add_field(name="randomanimesong", value="Sends a random anime song.", inline=False)
	helpembed.add_field(name="github", value="Private messages github link. (Developer only command)", inline=False)
	helpembed.add_field(name="todo", value="Private messages bot to-do list. (Developer only command)", inline=False)
	helpembed.set_thumbnail(url="https://cdn.discordapp.com/attachments/720598695191511110/721769409139703938/OmenaLogo.png")

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
	await ctx.channel.purge(limit=amount)

@client.command()
async def aboutme(ctx):
	await ctx.send("```Omena!BOT a4.0.5\n" + \
				   "Developed by:\n" + \
				   "MulfoK: Lead Programmer\n" + \
				   "lenrik1589: Programmer\n" + \
				   "General Purpose Discord Bot\n" + \
				   "Written in Python 3.8.2\n" + \
				   "help for commands list (~ is default prefix)```")

@client.command()
@commands.has_permissions(administrator=True)
#set params and kick
async def kick(ctx, member : discord.Member, *, reason=None):
	await member.kick(reason=reason)
	await ctx.send(f'{member.mention} was kicked from the server. :hammer:')
	print(f'{member} was kicked from a server!')

@client.command()
@commands.has_permissions(administrator=True)
#set params and BAN
async def ban(ctx, member : discord.Member, *, reason=None):
	await member.ban(reason=reason)
	await ctx.send(f'{member.mention} was banned from the server. :hammer:')
	print(f'{member} was banned from a server!')

@client.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
	#grab server ban list and return
	banned_users = await ctx.guild.bans()
	member_name, member_discriminator = member.split('#')

	for ban_entry in banned_users:
		user = ban_entry.user

		if (user.name, user.discriminator) == (member_name, member_discriminator):
			await ctx.guild.unban(user)
			await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
			print(f'{user.mention} was unbanned from a server.')
			return

#Developer Commands
##################################################################
#stops bot command
@client.command(aliases=["quit", "exit", "stop"])
#@commands.has_permissions(administrator=True)
async def close(ctx):
	if ctx.author.id == (465816879072542720 or 437296242817761292): #first id is mulfok, second is lenrik
		await ctx.send("Shutting down... See ya! :lock:")
		await client.close()
		print('Bot Closed By Developer')

	else:
		await ctx.send("You're not a developer! :x:")
		print("Someone tried to close the bot!")

#github link command (useful for if you lost the link or something)
@client.command()
async def github(ctx):
	if ctx.author.id == 437296242817761292 or 465816879072542720 or 691668587005607957: #first id is mulfok, second is lenrik, third is wullie
		await ctx.author.send("Github (Private): https://github.com/MulfoK/omenabot1.0\nShh... Let's not leak our hard work!")
		await ctx.send("You have been private messaged the github link. :white_check_mark:")
		print("Github pulled up by developer.")

	else:
		await ctx.send("You're not a developer! :x:")
		print("Someone tried to pull up the Github link!")

#todo command
@client.command()
async def todo(ctx):
	if ctx.author.id == 437296242817761292 or 465816879072542720 or 691668587005607957: #first id is mulfok, second is lenrik, third is wullie
		await ctx.author.send("I feel sorry for you developers...\n" + \
							  "```Our epic todo list:\n" + \
							  "1: Integrate a music player into Omena\n" + \
							  "2: Get a ~calc command working from a cog\n```"
							 )
		await ctx.send("The developer to-do list has been private messaged to you! :white_check_mark:")
		print("Todo list pulled up by developer")

	else:
		await ctx.send("You're not a developer! :x:")
		print("Someone tried to pull of the developer to-do list!")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#easter egg commands
#alcohol command
@client.command()
async def alcohol(ctx):
	if ctx.author.id == 397573419811602442: #karnage 397573419811602442
		await ctx.send("Go drink alcohol you madman. :beer:")

	else:
		await ctx.send("This command isn't for you! :x:")

#hack command
@client.command()
async def hack(ctx, *, hackvic):
	#setup random responses array
	hackcompanies = ["Mojang Studios",
					"Epic Games",
					"Microsoft",
					"Roblox Studios",
					"Google",
					"Canonical",
					"Facebook",
					"theist mother"
					]

	hacktasks = ["Grabbing 2TB 'Homework' folder...",
				f"Texting {hackvic}'s crush...",
				"Stealing payment information..."
				]

	hackpayment = ["£1.00",
				   "£25.00",
				   "£50.00",
				   "£75.00",
				   "£100.00",
				   "£1000.00"
				]
	#send messages in a timely order
	hack_message = await ctx.send(f"Hacking {hackvic}...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Grabbing 2TB 'Homework' folder...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Selling data to {random.choice(hackcompanies)}...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Laughing evilly...")
	await asyncio.sleep(2)
	await hack_message.edit(content="Bypassing Discord security...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Email: {hackvic}hasnofriends@hotmail.com\nPassword: ihateyouihateyougodie")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Reporting {hackvic} for breaking Discord TOS...")
	await asyncio.sleep(2)
	await hack_message.edit(content=f"Payment recieved: {random.choice(hackpayment)}")
	await asyncio.sleep(1)
	await ctx.send(f"The 100% real hack is complete.")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
##################################################################
#slap commands
@client.command()
async def slap(ctx, *, arg):
	await ctx.send(f"Slapped {arg}!")
#-----------------------------------
#error catch area
@client.event
async def on_command_error(ctx, error): 
	#checks to see if command is missing args, then sends message
	if isinstance(error, commands.MissingRequiredArgument):
		await ctx.send('Please fill all required arguments! :eyes:')
		return

	#checks to see if permissions all exist
	if isinstance(error, commands.MissingPermissions):
		await ctx.send("You're missing required permissions! :x:")
		print("Someone tried to run a command that they don't have permissions for!")
		return

	if isinstance(error, commands.BotMissingPermissions):
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

for filename in os.listdir('./cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')

client.run(config["discord_token"])
