import asyncio
import inspect
import json
import logging
import random
import re
from math import sin, cos, tan, sqrt, asin, acos, atan, ceil, floor, pow, degrees as deg, radians as rad

import discord
from discord.ext import commands

from main import OmenaBot


class General_commands(commands.Cog):
	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.general")
		self.bot = bot

	@commands.command()
	async def dnd(self, ctx: discord.ext.commands.Context, command: str, args):
		if not self.bot.servers[f'{ctx.guild.id}'].get("channels") is None:
			if not self.bot.servers[f'{ctx.guild.id}'].get("channels").get("dnd") is None:
				if not self.bot.servers[f'{ctx.guild.id}']["channels"]["dnd"] == ctx.channel.id:
					ctx.message.content = (await self.bot.get_prefix(ctx.message)) + " in_this_channel"
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
			embed.add_field(name="first stat", value=OmenaBot.get_stat())
			embed.add_field(name="second stat", value=OmenaBot.get_stat())
			embed.add_field(name="third stat", value=OmenaBot.get_stat())
			embed.add_field(name="fourth stat", value=OmenaBot.get_stat())
			embed.add_field(name="fifth stat", value=OmenaBot.get_stat())
			embed.add_field(name="sixth stat", value=OmenaBot.get_stat())
			await ctx.send(embed=embed)

	@commands.command(aliases=["setprefix"], help="Sets command prefix.\nOnly admins can use it.",
										brief="Sets command prefix.", hidden=False)
	async def changeprefix(self, ctx: discord.ext.commands.Context, prefix):
		if ctx.author.guild_permissions.administrator or not self.bot.config['devs'].get(f'{ctx.author.id}') is None:
			with open(f'{self.bot.rundir}/private/servers.json', 'r') as server_file:
				servers = json.load(server_file)

			self.logger.info(f'Prefix changed to {prefix} for server {ctx.guild.name} (ID {ctx.guild.id})')
			servers[str(ctx.guild.id)]['prefix'] = prefix
			servers[str(ctx.guild.id)]['name'] = str(ctx.guild.name)
			await ctx.send(f'Prefix changed to `{prefix}`! :white_check_mark:')

			with open(f'{self.bot.rundir}/private/servers.json', 'w') as server_file:
				json.dump(servers, server_file, indent=2)
		else:
			commands.MissingPermissions(ctx.author.guild_permissions.administrator)

	@commands.command(name="set", brief="Configuration command.", hidden=False)
	async def set_param(self, ctx: discord.ext.commands.Context, param: str, *value: str):
		"""
		Command for configuring different bot parameters for current  guild.
		"""
		try:
			if param == "permanick":
				if not ctx.author.guild_permissions.manage_nicknames and not ctx.author.guild_permissions.administrator and \
								self.bot.config["devs"].get(f"{ctx.author.id}") is None:
					raise commands.MissingPermissions(discord.permissions.Permissions(permissions=1 << 27))
				if len(ctx.message.mentions) == 1:
					member = ctx.message.mentions[0]
				elif len(value[0]) == len("564489099512381440"):
					member = ctx.guild.get_member(int(value[0]))
				else:
					member = ctx.guild.get_member(int(value[0][2:-1]))
				await ctx.message.delete()
				if self.bot.servers[f'{ctx.guild.id}'].get("nicks") is None:
					self.bot.servers[f'{ctx.guild.id}']["nicks"] = {}
				if len(value) < 2:
					if not self.bot.servers[f'{ctx.guild.id}']["nicks"].get(f'{member.id}') is None:
						self.bot.servers[f'{ctx.guild.id}']["nicks"].pop(f'{member.id}')
						await ctx.send(f"reset permanent nick for {member}", delete_after=3)
						await member.edit(nick=None)
				else:
					permanentnick = ' '.join(value[1:])
					if len(permanentnick) > 32:
						await ctx.send(f"Nickname `{permanentnick}` is too long (32 characters max).", delete_after=7)
						return
					self.bot.servers[f'{ctx.guild.id}']["nicks"][f'{member.id}'] = permanentnick
					await ctx.send(f"permanent nick for {member} is now set to `{permanentnick}`", delete_after=3)
					await member.edit(reason="no reason, lol", nick=permanentnick)
				with open(f'{self.bot.rundir}/private/servers.json', 'w') as f:
					json.dump(self.bot.servers, f, indent=2)
				return
			elif param == "channel":
				if ctx.author.guild_permissions.manage_channels or not self.bot.config["devs"].get(f"{ctx.author.id}") is None:
					if len(value) < 1:
						raise commands.MissingRequiredArgument(
							inspect.Parameter(name="chat", kind=inspect._ParameterKind.VAR_POSITIONAL))
					if len(value) < 2:
						raise commands.MissingRequiredArgument(
							inspect.Parameter(name="room", kind=inspect._ParameterKind.VAR_POSITIONAL))
					channel = ctx.channel
					try:
						chan_id = int(value[1][2:-1])
						channel = ctx.guild.get_channel(chan_id)
					except ValueError:
						if value[1] == "here":
							if self.bot.servers[f'{ctx.guild.id}'].get("channels") is None:
								self.bot.servers[f'{ctx.guild.id}']["channels"] = {}
							self.bot.servers[f'{ctx.guild.id}']["channels"][value[0]] = channel.id
							await ctx.send(f"Channel {value[0]} has been set to #{channel} for this guild.", delete_after=3)
							await asyncio.sleep(3)
							await ctx.message.delete()
							print(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
							self.logger.info(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
						elif value[1] == "unset":
							if self.bot.servers[f'{ctx.guild.id}'].get("channels") is None:
								await ctx.send("No channels are set for this guild.", delete_after=3)
								await asyncio.sleep(3)
								await ctx.message.delete()
								return
							elif self.bot.servers[f'{ctx.guild.id}']["channels"].get(value[0]) is None:
								await ctx.send("This channel is not set for this guild.", delete_after=3)
								await asyncio.sleep(3)
								await ctx.message.delete()
								return
							else:
								self.bot.servers[f'{ctx.guild.id}']["channels"][value[0]] = None
								await ctx.send(f"Channel {value[0]} has successfully unset for this guild.", delete_after=3)
								await asyncio.sleep(3)
								await ctx.message.delete()
								print(f"Channel {value[0]} has been unset for guild {ctx.guild}.")
								self.logger.info(f"Channel {value[0]} has been unset for guild {ctx.guild}.")
						else:
							print(f'not setting chat {value[0]} to anywhere as invalid parameters are passed in.')
					else:
						if self.bot.servers[f'{ctx.guild.id}'].get("channels") is None:
							self.bot.servers[f'{ctx.guild.id}']["channels"] = {}
						self.bot.servers[f'{ctx.guild.id}']["channels"][value[0]] = chan_id
						await ctx.send(f"Channel {value[0]} has been set to #{channel} for this guild.", delete_after=3)
						'[　　　　　　　　　ScrubPhantom　　　　　　　　　]'
						await asyncio.sleep(3)
						await ctx.message.delete()
						print(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
						self.logger.info(f"Channel {value[0]} has been set to #{channel} for guild {ctx.guild}.")
					with open(f'{self.bot.rundir}/private/servers.json', 'w') as f:
						json.dump(self.bot.servers, f, indent=2)
				else:
					commands.MissingPermissions(discord.permissions.Permissions(permissions=8))
			else:
				print(param)
		except discord.errors.Forbidden:
			with open(f'{self.bot.rundir}/private/servers.json', 'w') as f:
				json.dump(self.bot.servers, f, indent=2)

	@commands.command(name='dummy_log',
										help="Creates a dummy log of all types and prints message into console.\nCan only "
												 "be used by developer.", brief="Test if logging works.", hidden=True)
	async def dummy_log(self, ctx: discord.ext.commands.Context):
		attempt_id = ctx.author.id
		if attempt_id == 465816879072542720 or attempt_id == 437296242817761292:  # first id is mulfok, second is lenrik
			self.logger.debug("dummy debug log message")
			self.logger.info("dummy info log message")
			self.logger.warning("dummy warning log message")
			self.logger.error("dummy error log message")
			self.logger.critical("dummy critical log message")
			log = ctx.message.content.replace("\n", "\n> ")
			self.logger.info(f'actual message: {log}')
			print("{Fore.YELLOW}dummy message terminal")
			print("{Fore.GREEN}another message but\nspilt\ninto lines.")
			await ctx.send("debug log created", delete_after=1)
		await ctx.message.delete()

	@commands.command()
	async def pong(self, ctx: commands.context):
		# await
		if random.randrange(1000) < 947:
			await ctx.send("ping, :ping_pong:!")
		else:
			user, response = ctx.guild.get_member(self.bot.user.id), random.choice(self.bot.responses['pong_win'])
			if random.randrange(1000) < 493:
				user, response = ctx.author, random.choice(self.bot.responses['pong_loss'])
			name = user.nick
			if not name:
				name = user.name
			await ctx.send(f'{response}\n**{name}** is victorous')

	# Commands area
	@commands.command()
	async def ping(self, ctx: commands.context, *varg):
		if varg == ():
			# simply reply with 'Pong!' and milliseconds
			await ctx.send(f'Pong! {round(self.bot.latency * 1000)}ms')
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
			user_id = int(varg[3:-1])
			user = ctx.guild.get_member(user_id)
			enabled = self.bot.config['ping'][str(user_id)]
			if enabled is None:
				enabled = False
			if enabled:
				initial_pings = pings
				self.logger.warning(
					f"{ctx.author.name} (ID: {ctx.author.id}) requested to ping {user.name} {pings} times with delay of {delay}"
					f" seconds.")
				while pings > 0:
					pings -= 1
					if self.bot.stop_pings:
						pings = 0
						await ctx.send(f"<@{user.id}>, pings were stopped.")
					elif pings > 0:
						await ctx.send(
							f"<@{user.id}>, ping № {initial_pings - pings} out of {initial_pings}"
							f" (ETA:{self.bot.parse_duration(int(delay * pings))})")
					else:
						await ctx.send(f"<@{user.id}>, ping № {initial_pings - pings}. **last ping**.")
					await asyncio.sleep(delay)
			else:
				await ctx.send(f"Pinging `{user.name}` is not enabled but they can enable it if they want.")

	@commands.command(name="toggle")
	async def toggle(self, ctx: discord.ext.commands.Context, command: str, *varg: str):
		if command == "ping":
			if not ctx.message.mentions == []:
				user = ctx.message.mentions[0]  # int(varg[3:-1]))
			else:
				user = ctx.author
			enabled = self.bot.config['ping'].get(f'{user.id}')
			if enabled is None:
				enabled = False
			if ctx.author == user or ctx.author.guild_permissions.manage_messages:
				self.bot.config['ping'][f'{user.id}'] = not enabled
				with open(f'{self.bot.rundir}/private/bot.json', 'w') as file:
					json.dump(self.bot.config, file, indent=2)
				if enabled:
					response = await ctx.send(f"Pings successfully toggled for {user.name} (now disabled)")
				else:
					response = await ctx.send(f"Pings successfully toggled for {user.name} (now enabled)")
				await asyncio.sleep(3)
				await response.delete()
			else:
				response = await ctx.send(
					f"That's not how it works, you can't decide whether you can annoy {user.name} just because,"
					f" only {user.name} can :P")
				await asyncio.sleep(3)
				await response.delete()
		else:
			self.bot.output.write(str(type(self.bot.output)) + str(varg))

	@commands.command()
	async def pingtrue(self, ctx):
		# reply with "pong!" and DON'T round ms
		await ctx.send(f'Pong! {self.bot.latency * 1000}ms')

	# the F command
	@commands.command(name="f")
	async def f_command(self, ctx):
		# send image link

		fembed = discord.Embed(
			colour=discord.Colour.red()
		)
		fembed.set_author(name="Paying respects...")
		fembed.set_image(url=f"{random.choice(self.bot.responses['f'])}")

		await ctx.send(embed=fembed)

	# Random Anime Song Command
	@commands.command(aliases=["animesong"])
	async def randomanimesong(self, ctx):
		await ctx.send(f"The developers are not weebs I swear :eyes:\n{random.choice(self.bot.responses['anime'])}")

	@commands.command(name='8ball', aliases=['eightball'])
	async def _8ball(self, ctx, *, question):
		# output random answer
		await ctx.message.delete()
		await ctx.send(f'Question: "`{question}``" by {ctx.author.name}\nAnswer: {random.choice(self.bot.responses["8ball"])}')

	@commands.command()
	async def trivia(self, ctx):
		# output random answer
		await ctx.send(f'{random.choice(self.bot.responses["trivia"])}')

	@commands.command(brief="minecraft 1.15.2 commands")
	async def mcmd(self, ctx: discord.ext.commands.Context, *, page: int = 1):
		"""
		"""

		mcmdembed = discord.Embed(
			colour=discord.Colour.red()
		)
		if 0 < page <= len(self.bot.responses['mc_commands']):
			mcmdembed.set_author(name=f"1.15.2 Full Command Documentation Page {page}/{len(self.bot.responses['mc_commands'])}")
			mcmdembed.set_footer(text=f"1.15.2 Full Command Documentation Page {page}/{len(self.bot.responses['mc_commands'])}")
			for command in self.bot.responses['mc_commands'][page - 1]:
				mcmdembed.add_field(name=command, value=self.bot.responses['mc_commands'][page - 1][command], inline=False)
		else:
			await ctx.send(f"Sorry, there's no page №{page}")
			return

		await ctx.send(embed=mcmdembed)

	@commands.command()
	async def clear(self, ctx: discord.ext.commands.Context, amount: int):
		perms = ctx.message.author.permissions_in(ctx.channel)
		if perms.manage_messages or not self.bot.config["devs"].get(f"{ctx.author.id}") is None:
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
				await ctx.channel.purge(limit=amount + 1)
				await asyncio.sleep(0.1)
				success = await ctx.send(f"Removed {amount} messages! :white_check_mark:")
				await asyncio.sleep(1)
				await success.delete()
		else:
			commands.MissingPermissions(perms.manage_messages)

	@commands.command()
	async def aboutme(self, ctx):
		await ctx.send("```\nOmena!BOT v1.0.0\n" +
									 "Developed by:\n" +
									 "MulfoK: Lead Programmer\n" +
									 "lenrik1589: Debugger\n" +
									 "General Purpose Discord Bot\n" +
									 "Written in Python 3.8.2\n" +
									 "help for commands list (~ is default prefix)```")

	# Developer Commands
	##################################################################
	# stops bot command
	@commands.command(aliases=["quit", "exit"], hidden=True)
	async def close(self, ctx):
		if not self.bot.config["devs"].get(f"{ctx.author.id}") is None and \
						not self.bot.config["devs"][f"{ctx.author.id}"]["priveleges"].index("close") == -1:
			# first id is mulfok, second is lenrik
			await ctx.send("Shutting down... See ya! :lock:", delete_after=0.5)
			await asyncio.sleep(0.6)
			if not ctx.message.channel.type.name == 'private':
				await ctx.message.delete()
			await self.bot.close_bot(ctx.author.name, ctx.author.id)

		else:
			if not ctx.message.channel.type.name == 'private':
				self.logger.info(f"{ctx.author} (ID:{ctx.author.id}) tried to close the bot in {ctx.guild.name}#{ctx.channel}!")
			else:
				self.logger.info(f"{ctx.author} (ID:{ctx.author.id}) tried to close the bot in private messages!")
			await ctx.send("You're not a developer! :x:")
			print(f"{ctx.author} (ID: {ctx.author.id}) tried to close the bot!")

	# github link command (useful for if you lost the link or something)
	@commands.command(hidden=True)
	async def github(self, ctx):
		if not self.bot.config["devs"].get(f"{ctx.author.id}") is None:
			await ctx.author.send(
				"Github (Private): https://github.com/MulfoK/omenabot1.0\nShh... Let's not leak our hard work!")
			await ctx.send("You have been private messaged the github link. :white_check_mark:", delete_after=1)
			self.logger.info(f"Github pulled up by {ctx.author} ID: {ctx.author.id}")
			await asyncio.sleep(1)
			await ctx.message.delete()

		else:
			await ctx.send("You're not a developer! :x:")
			self.logger.info(f"{ctx.author} (ID {ctx.author.id}) tried to pull up github link!")

	# "todo" command
	@commands.command()
	async def todo(self, ctx):
		if not self.bot.config["devs"].get(f"{ctx.author.id}") is None:
			await ctx.author.send("I feel sorry for you developers...\n"
														"```Our epic todo list:\n"
														"1: Make music.py atleast work")
			await ctx.send("The developer to-do list has been private messaged to you! :white_check_mark:")
			self.logger.info(f"Todo list pulled up by {ctx.author} ID: {ctx.author.id}")

		else:
			await ctx.send("You're not a developer! :x:")
			self.logger.info(f"{ctx.author} (ID: {ctx.author.id}) tried to pull of the developer to-do list!")

	#######################################################
	# calc command
	@commands.command(brief="calculate your expressions", usage="expression")
	async def calc(self, ctx: discord.ext.commands.Context, *equation: str):
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

		not_escaped_equation = [re.sub(r"\\$", " ", s, 0, re.MULTILINE) for s in equation]
		print(not_escaped_equation)
		spliced_equation = " ".join(not_escaped_equation)
		variables = {
			"sin": sin,
			"cos": cos,
			"tan": tan,
			"sqrt": sqrt,
			"asin": asin,
			"acos": acos,
			"atan": atan,
			"ceil": ceil,
			"floor": floor,
			"pow": pow,
			"deg": deg,
			"rad": rad
		}
		variable_decl_reg_ex = r"(?:(\w*)=;)"
		matches = re.finditer(variable_decl_reg_ex, spliced_equation, re.MULTILINE)
		spliced_equation = re.sub(variable_decl_reg_ex, "", spliced_equation, 0, re.MULTILINE)

		for _, match in enumerate(matches, start=1):
			variables[match.group(1)] = None

		try:
			result = eval(spliced_equation, variables)
		except NameError:
			await ctx.send("error evaluating your expression:\n\tuse of variables is not implemented.")
			return
		except Exception as e:
			await ctx.send("%s" % e)
			return
		print(result)
		spliced_equation = spliced_equation.replace("*", "\*")
		await ctx.send(f"{spliced_equation} = {result}")

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# easter egg commands
	# alcohol command
	@commands.command(hidden=True)
	async def alcohol(self, ctx):
		if ctx.author.id == 397573419811602442:  # karnage 397573419811602442
			await ctx.seyound("Go drink alcohol you madman. :beer:")

		else:
			await ctx.send("This command isn't for you! :x:")

	@commands.command(hidden=True, name="best_free_opensource_3d_modelling_sculpting_drawing_and_even_more_software",
										aliases=["blend", "blender", "smoothie_maker"])
	async def blender(self, ctx):
		emb = discord.Embed(
			title="**Blender**",
			description="is a free and open-source 3D computer graphics software toolset…"
									"\n~~shamelessly stolen from en.wikipedia.org/Blender_(software)~~"
		)
		emb.set_author(name="Blender Foundation", url="https://www.blender.org",
									 icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb"
														"/0/0c/Blender_logo_no_text.svg/512px-Blender_logo_no_text.svg.png")
		await ctx.send(embed=emb)
		await ctx.message.delete()

	# coffee command
	@commands.command(hidden=True)
	async def coffee(self, ctx):
		if ctx.author.id == 721045183982207046:  # lenrick 721045183982207046
			await ctx.send("Go drink coffee you madman. :coffee:")

		else:
			await ctx.send("This command isn't for you! :x:")

	# ifstatment command
	@commands.command(name="if", hidden=True)
	async def _if(self, ctx):
		if ctx.author.id == 465816879072542720:
			await ctx.send("Go learn if statments you madman. :dagger:")

		else:
			await ctx.send("This command isn't for you! :x:")

	# hack command
	@commands.command(hidden=True)
	async def hack(self, ctx: discord.ext.commands.Context, *, hackvic):
		message: discord.Message = ctx.message
		# store homework amount in temp variable
		homeworkstorage = random.choice(self.bot.responses["hack"]["homework"])
		# send messages in a timely order
		hack_message = await ctx.send(f"Hacking {hackvic}...")
		await asyncio.gather(asyncio.sleep(2), message.delete())
		await hack_message.edit(content=f"Grabbing {homeworkstorage} 'Homework' folder...")
		await asyncio.sleep(2)
		await hack_message.edit(content=f'Selling data to {random.choice(self.bot.responses["hack"]["companies"])}...')
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Payment recieved: {random.choice(self.bot.responses['hack']['payment'])}")
		await asyncio.sleep(2)
		await hack_message.edit(content="Bypassing Discord security...")
		await asyncio.sleep(2)
		mail_before, mail_after = random.choice(self.bot.responses['hack']['mail_body'])
		await hack_message.edit(
			content=f"Email: {mail_before}{hackvic}{mail_after}@{random.choice(self.bot.responses['hack']['mail_provider'])}"
							f"\nPassword: ihateyouihateyougodie")
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Reporting {hackvic} for breaking Discord TOS...")
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Laughing evilly...")
		await asyncio.sleep(2)
		await ctx.send(f"The 100% real hack of {hackvic} is complete.")
		await ctx.send(f"Homework folder size: {homeworkstorage}")

	@commands.command(hidden=True)
	async def slap(self, ctx, *, person: discord.User):
		await ctx.send(f"Slapped {person}!")

	# joke command
	@commands.command(name="joke", brief="…tells a joke.", help="Blame <@465816879072542720> for it's all his fault")
	async def joke(self, ctx):
		joke_line, punchline = random.choice(self.bot.responses["jokes"])
		message = await ctx.send(joke_line)
		await asyncio.sleep(2)
		await message.edit(content=joke_line + "\n" + punchline)


def setup(bot):
	bot.add_cog(General_commands(bot))
