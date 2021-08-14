import asyncio
import inspect
import json
import logging
import random
import re
from datetime import datetime
from math import sin, cos, tan, sqrt, asin, acos, atan, ceil, floor, pow, degrees as deg, radians as rad, pi

import discord
from colorama import Fore
from discord.ext import commands

from omenabot import OmenaBot
from utils import misc


class General(commands.Cog):

	@property
	def qualified_name(self):
		return "General commands"

	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.general")
		self.bot = bot

	@commands.Cog.listener("on_ready")
	async def restart_tasks(self):
		subs = []
		for guild in self.bot.data.profiles:
			pass
		await asyncio.gather(*subs)
		pass

	# @remcmd
	@commands.command()
	async def dnd(self, context: discord.ext.commands.Context, command: str, *args, **kwargs):
		if "channels" in self.bot.data.profiles[f'{context.guild.id}']:
			if "dnd" in self.bot.data.profiles[f'{context.guild.id}']["channels"]:
				if not self.bot.data.profiles[f'{context.guild.id}']["channels"]["dnd"] == context.channel.id:
					context.message.content = (await self.bot.get_prefix(context.message)) + " in_this_channel"
					raise commands.CommandNotFound()
		if command == "roll":
			await self.roll(context, *args, **kwargs)
		if command == "dice":
			await self.dice(context, *args, **kwargs)

	@commands.command(hidden=True)
	async def roll(self, context: discord.ext.commands.Context, sides: int):
		if sides < 1:
			raise commands.BadArgument(' "whole positive nuber', "Unable to throw imaginary dice")
		j = random.randrange(sides) + 1
		await context.send(f'your number is: {j}')

	@commands.command(hidden=True)
	async def dice(self, context: discord.ext.commands.Context):
		embed = discord.Embed()
		embed.set_author(name=context.author.name, icon_url=context.author.avatar_url)
		embed.add_field(name="first stat", value=misc.get_stat())
		embed.add_field(name="second stat", value=misc.get_stat())
		embed.add_field(name="third stat", value=misc.get_stat())
		embed.add_field(name="fourth stat", value=misc.get_stat())
		embed.add_field(name="fifth stat", value=misc.get_stat())
		embed.add_field(name="sixth stat", value=misc.get_stat())
		await context.send(embed=embed)

	@commands.command(aliases=["setprefix"], help="Sets command prefix.\nOnly admins can use it.",
	                  brief="Sets command prefix.", hidden=True)
	async def changeprefix(self, context: discord.ext.commands.Context, prefix):
		if context.author.guild_permissions.manage_messages or f'{context.author.id}' in self.bot.data.bot['devs']:
			gid = f"{context.guild.id}"
			self.logger.info(f'Prefix changed to {prefix} for server {context.guild.name} (ID {gid})')
			self.bot.data.profiles[gid]['prefix'] = prefix
			await context.send(f'Prefix changed to `{prefix}`! :white_check_mark:')

			self.bot.data.save_server(context.guild.id)
		else:
			commands.MissingPermissions(context.author.guild_permissions.manage_messages)

	@commands.command()
	async def uptime(self, content: commands.Context):
		import psutil, os
		await content.send("bot uptime is "
		                   f"{misc.parse_duration(datetime.now().timestamp() - psutil.Process(os.getpid()).create_time())}")

	@commands.command(name="set", brief="Configuration command.", hidden=False, qualified_name="set")
	async def set_param(self, context: discord.ext.commands.Context, param: str, *value: str):
		"""
		Command for configuring different bot parameters for current  guild.
		"""
		gid = f'{context.guild.id}'
		try:
			match param, value:
				case "prefix", [* prefix]:
					await self.changeprefix(context, " ".join(prefix))
				case "prefix", None:
					raise commands.MissingRequiredArgument(
						inspect.Parameter(name="prefix", kind=inspect.Parameter.VAR_POSITIONAL))
				case "permanick", None:
					raise commands.MissingRequiredArgument(inspect.Parameter(name="nick", kind=inspect.Parameter.VAR_POSITIONAL))
				case "permanick", (_, * _):
					cog = self.bot.get_cog("UserManagement")
					command = cog.setnick
					await command(context, *value)
				case "channel", None:
					raise commands.MissingRequiredArgument(inspect.Parameter(name="chat", kind=inspect.Parameter.VAR_POSITIONAL))
				case "channel", ():
					raise commands.MissingRequiredArgument(inspect.Parameter(name="room", kind=inspect.Parameter.VAR_POSITIONAL))
				case "channel", (chat, "here"):
					channel = context.channel
					self.bot.data.profiles[gid].setdefault("channels", {})[chat] = channel.id
					await context.send(f"Channel {chat} has been set to #{channel} for this guild.", delete_after=3)
					await context.message.delete(delay=3)
					print(f"Channel {chat} has been set to #{channel} for guild {context.guild}.")
					self.logger.info(f"Channel {chat} has been set to #{channel} for guild {context.guild}.")
				case "channel", (chat, "unset"):
					if "channels" not in self.bot.data.profiles[gid]:
						await context.send("No channels are set for this guild.", delete_after=3)
						await context.message.delete(delay=3)
					elif chat not in self.bot.data.profiles[gid]["channels"]:
						await context.send("This channel is not set for this guild.", delete_after=3)
						await context.message.delete(delay=3)
					else:
						del self.bot.data.profiles[gid]["channels"][chat]
						await context.send(f"Channel {chat} has successfully unset for this guild.", delete_after=3)
						await context.message.delete(delay=3)
						print(f"Channel {chat} has been unset for guild {context.guild}.")
						self.logger.info(f"Channel {chat} has been unset for guild {context.guild}.")
				case "channel", (chat, * room):
					if context.author.guild_permissions.manage_channels or f"{context.author.id}" in self.bot.data.bot["devs"]:
						channel = misc.find_channel(context, room)
						self.bot.data.profiles[gid].setdefault("channels", {})[chat] = channel.id
						await context.send(f"Channel {chat} has been set to #{channel} for this guild.", delete_after=3)
						await context.message.delete(delay=3)
						print(f"Channel {chat} has been set to #{channel} for guild {context.guild}.")
						self.logger.info(f"Channel {chat} has been set to #{channel} for guild {context.guild}.")
					else:
						raise commands.MissingPermissions(discord.Permissions(permissions=discord.Permissions.manage_channels))
				case _, _:
					print(param, value)
					return
			self.bot.data.save_server(context.guild.id)
		except discord.errors.Forbidden:
			self.bot.data.save_server(context.guild.id)

	@commands.guild_only()
	@commands.command(
		name='dummy_log',
		help="""
		Creates a dummy log of all types and prints message into console.
		Can only be used by developer.""",
		brief="Test if logging works.",
		hidden=True
	)
	async def dummy_log(self, context: discord.ext.commands.Context):
		attempt_id = context.author.id
		if attempt_id in [465816879072542720, 437296242817761292, 746090211087351900]:
			# first id is mulfok, second is lenrik, third is Alice
			self.logger.debug("dummy debug log message")
			self.logger.info("dummy info log message")
			self.logger.warning("dummy warning log message")
			self.logger.error("dummy error log message")
			self.logger.critical("dummy critical log message")
			log = context.message.content.replace("\n", "\n> ")
			self.logger.info(f'actual message: {log}')
			print(f"{Fore.YELLOW}dummy message terminal")
			print(f"{Fore.GREEN}another message but\nspilt\ninto lines.")
			await context.send("debug log created", delete_after=1)
		await context.message.delete()

	@commands.command()
	async def pong(self, context: commands.context):
		# await
		if random.randrange(1000) < 947:
			await context.send("ping, :ping_pong:!")
		else:
			user, response = context.guild.get_member(self.bot.user.id), random.choice(self.bot.data.responses['pong_win'])
			if random.randrange(1000) < 493:
				user, response = context.author, random.choice(self.bot.data.responses['pong_loss'])
			await context.send(f'{response}\n**{user.display_name}** is victorous')

	# Commands area
	@commands.command()
	async def ping(self, context: commands.context, *args):
		user, pings, delay = (None, None, None)
		try:
			match args:
				case():
					await context.send(f'Pong! ({round(self.bot.latency * 1000)}ms)')
					return
				case[user]:
					pings = delay = 1
				case[user, pings] if (pings := int(pings)) in range(0, 100):
					delay = 1
				case[user, pings, delay] if (pings := int(pings)) in range(0, 100) and (delay := int(delay)) >= 1:
					pass
				case _:
					print(args)
					raise commands.BadArgument()
		except ValueError as ve:
			raise commands.BadArgument() from ve
		user = misc.find_member(context.message, user)
		enabled = self.bot.data.bot['ping'].setdefault(f'{user.id}', False)
		if enabled:
			initial_pings = pings
			self.logger.warning(
				f"{context.author.name} (ID: {context.author.id}) "
				f"requested to ping {user.name} "
				f"{pings} times with delay of {delay} seconds."
			)
			await asyncio.sleep(delay)
			while pings > 0:
				pings -= 1
				if self.bot.stop_pings:
					pings = 0
					await context.send(f"<@{user.id}>, pings were stopped.")
				elif pings > 0:
					await context.send(
						f"<@{user.id}>, ping № {initial_pings - pings} out of {initial_pings}"
						f" (ETA:{misc.parse_duration(int(delay * pings))})")
					await asyncio.sleep(delay)
			else:
				await context.send(f"<@{user.id}>, ping № {initial_pings - pings}. **last ping**.")
				await asyncio.sleep(delay)
		else:
			await context.send(f"Pinging `{user.name}` is not enabled but they can enable it if they want.")

	@commands.command(name="toggle")
	async def toggle(self, context: discord.ext.commands.Context, command: str, *arg):
		if command == "ping":
			user = misc.find_member(context.message, arg[0])
			user = user if user else context.author
			enabled = self.bot.data.bot['ping'].get(f'{user.id}')
			if not enabled:
				enabled = False
			if context.author == user or \
							context.author.guild_permissions.manage_messages or \
							f"{context.author.id}" in self.bot.data.bot['devs']:
				self.bot.data.bot['ping'][f'{user.id}'] = not enabled
				with open(f'{self.bot.rundir}/private/bot.json', 'w') as file:
					json.dump(self.bot.data.bot, file, indent=2)
				if enabled:
					response = await context.send(f"Pings successfully toggled for {user.name} (now disabled)")
				else:
					response = await context.send(f"Pings successfully toggled for {user.name} (now enabled)")
				await asyncio.sleep(3)
				await response.delete()
			else:
				response = await context.send(
					f"That's not how it works, you can't decide whether you can annoy {user.name} just because,"
					f" only {user.name} can :P")
				await asyncio.sleep(3)
				await response.delete()
		else:
			self.bot.output.write(str(type(self.bot.output)) + str(arg))

	@commands.command()
	async def pingtrue(self, context):
		# reply with "pong!" and DON'T round ms
		await context.send(f'Pong! {self.bot.latency * 1000}ms')

	# the F command
	@commands.command(name="f")
	async def f_command(self, context):
		# send image link

		fembed = discord.Embed(
			colour=discord.Colour.red()
		)
		fembed.set_author(name="Paying respects...")
		fembed.set_image(url=f"{random.choice(self.bot.data.responses['f'])}")

		await context.send(embed=fembed)

	# Random Anime Song Command
	@commands.command(aliases=["animesong", "anime"])
	async def randomanimesong(self, context):
		await context.send(
			f"The developers are not weebs I swear :eyes:\n{random.choice(self.bot.data.responses['anime'])}")

	@commands.command(name='8ball', aliases=['eightball'])
	async def _8ball(self, context: commands.Context, *, question):
		# output random answer
		await context.message.delete()
		await context.send(
			f'Question: "`{question}`" by {context.author.name}\nAnswer: {random.choice(self.bot.data.responses["_8ball"])}')

	@commands.command()
	async def trivia(self, context: commands.Context):
		# output random answer
		await context.send(f'{random.choice(self.bot.data.responses["trivia"])}')

	@commands.command(brief="minecraft 1.15.2 commands")
	async def mcmd(self, context: discord.ext.commands.Context, *, page: int = 1):
		"""
		"""

		mcmdembed = discord.Embed(
			colour=discord.Colour.red()
		)
		if 0 < page <= len(self.bot.data.responses['mc_commands']):
			mcmdembed.set_author(
				name=f"1.15.2 Full Command Documentation Page {page}/{len(self.bot.data.responses['mc_commands'])}")
			mcmdembed.set_footer(
				text=f"1.15.2 Full Command Documentation Page {page}/{len(self.bot.data.responses['mc_commands'])}")
			for command in self.bot.data.responses['mc_commands'][page - 1]:
				mcmdembed.add_field(name=command, value=self.bot.data.responses['mc_commands'][page - 1][command], inline=False)
		else:
			await context.send(f"Sorry, there's no page №{page}")
			return

		await context.send(embed=mcmdembed)

	@commands.command()
	async def clear(self, context: discord.ext.commands.Context, amount: int):
		perms = context.channel.permissions_for(context.author)
		if perms.manage_messages or f"{context.author.id}" in self.bot.data.bot["devs"]:
			message = context.message
			if amount < 0:
				error = await context.send("That's not a valid arguement! :x:")
				await asyncio.sleep(1)
				await asyncio.gather(message.delete(), error.delete())
			elif amount > 100:
				error = await context.send("Purge limit is 100! :x")
				await asyncio.sleep(1)
				await asyncio.gather(message.delete(), error.delete())
			else:
				# for i in range(amount):
				# 	context.channel
				await context.channel.purge(limit=amount + 1)
				await asyncio.sleep(0.1)
				await context.send(f"Removed {amount} messages! :white_check_mark:", delete_after=1)
		else:
			commands.MissingPermissions(perms.manage_messages)

	@commands.command(hidden=True)
	async def delete(self, context: commands.Context, message: discord.Message):
		if not (f"{context.author.id}" in self.bot.data.bot["devs"] and message.author.id in self.bot.data.bot["devs"] + [
			self.bot.user.id]):
			return
		if context.guild:
			await context.message.delete()
		await message.delete()

	@commands.command()
	async def about(self, context: commands.Context):
		await context.send(
			f"""```
			Omena!BOT v1.0.0
			Developed by:
			MulfoK: Lead Programmer
			lenrik1589: Debugger
			General Purpose Discord Bot
			Written in Python 3.8.2
			help for commands list (~ is default prefix, {context.prefix} is current)```""")

	# Developer Commands
	##################################################################
	# stops bot command
	@commands.command(aliases=["quit", "exit"], hidden=True)
	async def close(self, context: commands.Context):
		if f"{context.author.id}" in self.bot.data.bot["devs"] and \
						"close" in self.bot.data.bot["devs"][f"{context.author.id}"]["privileges"]:
			# first id is mulfok, second is lenrik
			await context.send("Shutting down... See ya! :lock:", delete_after=0.5)
			await asyncio.sleep(0.6)
			if not context.message.channel.type.name == 'private':
				await context.message.delete()
			await self.bot.close_bot(context.author.name, context.author.id)

		else:
			if not context.message.channel.type.name == 'private':
				self.logger.info(
					f"{context.author} (ID:{context.author.id}) tried to close the bot in {context.guild.name}#{context.channel}!")
			else:
				self.logger.info(f"{context.author} (ID:{context.author.id}) tried to close the bot in private messages!")
			await context.send("You're not a developer! :x:")
			print(f"{context.author} (ID: {context.author.id}) tried to close the bot!")

	# github link command (useful for if you lost the link or something)
	@commands.command(hidden=True)
	async def github(self, context):
		if f"{context.author.id}" in self.bot.data.bot["devs"]:
			await context.author.send(
				"Github (Private): https://github.com/MulfoK/omenabot1.0\nShh... Let's not leak our hard work!")
			await context.send("You have been private messaged the github link. :white_check_mark:", delete_after=1)
			self.logger.info(f"Github pulled up by {context.author} ID: {context.author.id}")
			await asyncio.sleep(1)
			await context.message.delete()

		else:
			await context.send("You're not a developer! :x:")
			self.logger.info(f"{context.author} (ID {context.author.id}) tried to pull up github link!")

	# "todo" command
	@commands.command()
	async def todo(self, context):
		if f"{context.author.id}" in self.bot.data.bot["devs"]:
			await context.author.send("I feel sorry for you developers...\n"
			                          "```Our epic todo list:\n"
			                          "1: Make music.py atleast work")
			await context.send("The developer to-do list has been private messaged to you! :white_check_mark:")
			self.logger.info(f"Todo list pulled up by {context.author} ID: {context.author.id}")

		else:
			await context.send("You're not a developer! :x:")
			self.logger.info(f"{context.author} (ID: {context.author.id}) tried to pull of the developer to-do list!")

	#######################################################
	# calc command
	@commands.command(brief="calculate your expressions", usage="expression")
	async def calc(self, context: discord.ext.commands.Context, *equation: str):
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
		PI good old pi
		"""

		print(equation)
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
			"rad": rad,
			"PI": pi,
			"__builtins__": None
		}
		variable_decl_reg_ex = r"(?:(\w*)=;)"
		matches = re.finditer(variable_decl_reg_ex, spliced_equation, re.MULTILINE)
		spliced_equation = re.sub(variable_decl_reg_ex, "", spliced_equation, 0, re.MULTILINE)
		spliced_equation = spliced_equation.replace(";;", "\n")

		print(spliced_equation)

		for _, match in enumerate(matches, start=1):
			variables[match.group(1)] = None

		try:
			result = eval(spliced_equation, variables)
		except NameError:
			await context.send("error evaluating your expression:\n\tuse of variables is not implemented.")
			return
		except Exception as e:
			import traceback
			await context.send(f"""{'''
'''.join(traceback.format_exception(e))}""")
			return
		print(result)
		spliced_equation = spliced_equation.replace("*", "\*")
		await context.send(f"{spliced_equation} = {result}")

	@commands.command(hidden=True, name="best_free_opensource_3d_modelling_sculpting_drawing_and_even_more_software",
	                  aliases=["blend", "blender", "smoothie_maker"])
	async def blender(self, context):
		emb = discord.Embed(
			title="**Blender**",
			description="is a free and open-source 3D computer graphics software toolset…"
			            "\n~~shamelessly stolen from en.wikipedia.org/Blender_(software)~~"
		)
		emb.set_author(name="Blender Foundation", url="https://www.blender.org",
		               icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb"
		                        "/0/0c/Blender_logo_no_text.svg/512px-Blender_logo_no_text.svg.png")
		await context.send(embed=emb)
		await context.message.delete()


def setup(bot):
	bot.add_cog(General(bot))
