import logging
import os
import pathlib
import random
import sys
import time
import traceback
from itertools import cycle

import asyncio

import discord
import regex
from colorama import Fore, Style, init as init_terminal_styling
from discord.ext import commands, tasks

# List comprehesions: wanted_roles = [i[7:] for i in message.content.split("\n")]
# Lambdas: wanted_roles = list(map(lambda i: i[7:], message.content.split("\n")))
from utils import DoubleIO, BufferIO, data


class OmenaBot(commands.bot.Bot):

	# grabs server prefix from each server
	async def get_prefix(self, message: discord.Message):
		"""

		:param message:
		:return: prefix for :param message:
		"""
		if not message.guild:
			return '.'
		return self.data.bot.setdefault("prefix_overrides", {}).get(self.token) or self.data.profiles[
			str(message.guild.id)].setdefault("prefix", "~")

	status = cycle(['help - Brings up commands', 'aboutme - Shows bot info', 'trivia - Fun facts!',
	                'set prefix - Customise server prefix!', 'Ping me to get prefix on the server'])

	# Various debug console message events
	async def on_connect(self):
		self.logger.info('Connected to discord...')

	async def on_disconnect(self):
		self.logger.info('Disconnected from discord.')

	async def on_ready(self):
		# set status, change activity and print ready and start loop
		self.change_status.restart()
		await self.change_presence(status=discord.Status.online, activity=discord.Game('~help for commands!'))
		self.logger.info(f'Logged in as {self.user.name}')
		self.logger.info(f'Client ID: {self.user.id}')
		self.logger.info('---------')
		print(f"{Fore.GREEN}Ready")

	# Set default command prefix on server join
	async def on_guild_join(self, guild):
		self.logger.info(f'Bot joined {guild.name} (ID: {guild.id})')
		print(f'{Fore.MAGENTA}Bot has joined {guild.name} (ID: {guild.id})!')
		self.data.profiles[f"{guild.id}"] = self.data.profiles.setdefault(f"{guild.id}", {})

	async def on_member_join(self, member: discord.Member):
		if member.guild.id == 663903542842490910:
			print(f"{Fore.MAGENTA}{member} joined testman")
		else:
			self.logger.info(f'{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')
			print(f'{Fore.GREEN}{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')
		await asyncio.sleep(random.gammavariate(1.6, 0.8) * 2)
		self.data.profiles[f'{member.guild.id}'].setdefault("channels", {})
		if "welcomes" in self.data.profiles[f'{member.guild.id}']["channels"]:
			await member.guild.get_channel(int(self.data.profiles[f'{member.guild.id}']["channels"]["welcomes"])).send(
				random.choice(self.data.responses["hello"]).format(member))
		elif member.guild.system_channel:
			await member.guild.system_channel.send(random.choice(self.data.responses["hello"]).format(member))

	async def on_member_remove(self, member: discord.Member):
		if self.data.profiles[f'{member.guild.id}'].get('name') is None:
			self.data.profiles[f'{member.guild.id}']['name'] = member.guild.name
		if member.guild.id == 663903542842490910:
			print(f"{Fore.MAGENTA}{member} left testman")
		else:
			self.logger.info(f'{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')
			print(f'{Fore.RED}{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')
		await asyncio.sleep(random.gammavariate(1.6, 0.8) * 2)
		if "channels" in self.data.profiles[f'{member.guild.id}'] and "welcomes" in \
						self.data.profiles[f'{member.guild.id}'][
							"channels"]:
			await member.guild.get_channel(int(self.data.profiles[f'{member.guild.id}']["channels"]["welcomes"])).send(
				random.choice(self.data.responses["bye"]).format(member))
		elif member.guild.system_channel:
			await member.guild.system_channel.send(random.choice(self.data.responses["bye"]).format(member))

	# Tasks Area
	@tasks.loop(seconds=5)
	async def change_status(self):
		await self.change_presence(activity=discord.Game(next(self.status)))

	async def on_message(self, message: discord.Message):
		if not message.author == self.user:
			ctx: commands.Context = await self.get_context(message)
			if not message.guild:
				if not message.author.bot and message.content:
					await self.invoke(ctx)
					if not (ctx.command or ctx.invoked_with):
						await message.channel.send(
							r"I'm a bot, and certanly not smart enough to talk to you, my friend ¯\\\_(°^°)\_/¯",
							delete_after=5)
			else:
				if ctx.prefix and (ctx.command or regex.match("^" + ctx.prefix + r"\p{L}", message.content)):
					await self.invoke(ctx)
				if 'channels' in self.data.profiles[f'{message.guild.id}']:
					channels = self.data.profiles[f'{message.guild.id}']["channels"]
					if 'image-only' in channels:
						image_only = channels['image-only']
						if message.channel.permissions_for(message.guild.get_member(self.user.id)).manage_messages:
							if (message.channel.id in image_only) if isinstance(image_only, list) else (
											message.channel.id == image_only):
								if not message.attachments:
									if not ctx.command:
										# commands_cog = self.get_cog("General")
										# if commands_cog:
										# 	await commands_cog.delete(ctx, message)
										# else:
										await message.delete()
										return

				if message.content.startswith(self.user.mention):
					if message.content.rstrip(self.user.mention + " ") == "guilds":
						await message.delete()
						guilds = ""
						for guild in self.guilds:
							guilds = "\n".join([guilds, guild.name + f' (ID: {guild.id})'])
						await message.author.send(
							f"Currently i'm in {len(self.guilds)}, which are ```fix\n{guilds}\n```")
					else:
						await message.delete()
						self.logger.info(f"Bot was pinged in {message.guild.id}, by {message.author.id}")
						await message.channel.send(f'Current prefix is "`{await self.get_prefix(message)}`"')

	@staticmethod
	@commands.command(name="cog")
	async def cog(context: commands.Context, action: str, name: str = None):
		self = context.bot
		index = 0
		try:
			index = int(name)
			name = list(self.extensions.keys())[index][5:]
		except IndexError:
			print(f"index {index} is {'more than number of extensions' if index > len(self.extensions) else 'less than 0'}")
		except (ValueError, TypeError):
			pass
		if action in ["load", "unload", "reload"] and f"{context.author.id}" in self.data.bot["devs"] and name:
			if context.guild:
				await context.message.delete()
			try:
				print(action + "ing", name, "requested by", context.author.name, end="… ", flush=True)
				await asyncio.sleep(0)
				t = time.perf_counter()
				{
					"load": self.load_extension,
					"unload": self.unload_extension,
					"reload": self.reload_extension,
				}[action](f'cogs.{name}')
				self.logger.info(f"extension {name} loaded by {context.author.name}")
				print(f"{action}ed. (took {time.perf_counter() - t:1.5f} seconds)", end="")
			except commands.ExtensionNotFound:
				print("not loaded", end="")
				await context.send(f"cog {name} is not found")
			except commands.ExtensionNotLoaded:
				print("not loaded", end="")
				await context.send(f"cog {name} is not loaded")
			except commands.ExtensionAlreadyLoaded:
				print("already  loaded", end="")
				await context.send(f"cog {name} is already loaded")
			except commands.NoEntryPointError:
				print("no setup in " + name)
				await context.send(f"check your code, you forgot setup(bot) in {name}")
			except commands.ExtensionFailed as e:
				print(f'''exception {e.original} occurred while loading extension {name}
{"""
""".join(traceback.format_exception(e.original))}''', end="")
				await context.send(f'''exception {e.original} occurred while loading extension {name}```py
{"""
""".join(traceback.format_exception(e.original))}```''')
			finally:
				print("")
		elif action == "list":
			await context.send(
				"\n".join([f'{num}: {ext.__package__}/{ext.__name__.lstrip(ext.__package__)[1:]}' for num, ext in
				           enumerate(self.extensions.values())]))

	def __init__(self, token_name=None, *, no_load=[], gui=False, debug=False, **options):
		# noinspection PyUnresolvedReferences
		intents = discord.Intents.default()
		intents.members = True
		intents.reactions = True
		# intents.typing = True
		# intents.presences = True
		super().__init__(self.get_prefix, intents=intents, **options)
		self.debug = None
		self.token = token_name

		self.start_time_ns: int = 0
		self.start_time = ""

		self.output = DoubleIO(BufferIO(), sys.stdout)
		sys.stdout = self.output
		init_terminal_styling(autoreset=True)
		now = time.gmtime()
		self.init_time_ns = time.monotonic_ns()
		self.init_time = f'{now[0]}_{now[1]:02d}_{now[2]:02d}_{now[3]:02d}_{now[4]:02d}_{now[5]:02d}'
		print(f"Initialized at {Style.BRIGHT}{Fore.YELLOW}{self.init_time}{Style.NORMAL}{Fore.RESET}")

		self.rundir = pathlib.Path(__file__, ).parent.parent.absolute()
		self.home = os.getenv('HOME')

		try:
			stats = os.stat(self.rundir / f"python/logs/{self.token}_latest.log")
			created = time.gmtime(stats.st_ctime)
			created_time = f'{created[0]}_{created[1]:02d}_{created[2]:02d}_{created[3]:02d}_{created[4]:02d}_{created[5]:02d}'
			os.rename(
				self.rundir / f"python/logs/{self.token}_latest.log",
				self.rundir / f"python/logs/{created_time}_{self.token}.log"
			)
		except FileNotFoundError:
			print(f"{Style.DIM}No latest log.{Style.NORMAL}")

		try:
			stats = os.stat(self.rundir / f"python/logs/debug_{self.token}_latest.log")
			created = time.gmtime(stats.st_ctime)
			created_time = f'{created[0]}_{created[1]:02d}_{created[2]:02d}_{created[3]:02d}_{created[4]:02d}_{created[5]:02d}'
			os.rename(
				self.rundir / f"python/logs/debug_{self.token}_latest.log",
				self.rundir / f"python/logs/{created_time}_{self.token}_debug.log"
			)
		except FileNotFoundError:
			print(f"{Style.DIM}No latest debug log.{Style.NORMAL}")

		from logging import config as lonfig
		lonfig.dictConfig({
			"version": 1,
			'disable_existing_loggers': False,
			"formatters": {
				"default": {
					"format": "[%(asctime)s] [%(threadName)s|%(name)-16s/%(levelname)-8s] %(message)s"
				},
				"brief": {
					"format": "%(levelname)-8s: %(message)s"
				}
			},
			'handlers': {
				"console": {
					"class": "logging.StreamHandler",
					"formatter": "brief",
					"stream": self.output,
					"level": 0 if self.debug else "INFO"
				},
				"info": {
					"class": "logging.FileHandler",
					"filename": f'{self.rundir}/python/logs/{self.token}_latest.log',
					"formatter": "default",
					"level": "INFO"
				},
				"verbose": {
					"class": "logging.FileHandler",
					"filename": f'{self.rundir}/python/logs/debug_{self.token}_latest.log',
					"formatter": "default"
				}
			},
			"loggers": {
				'': {
					"level": 0,
					"handlers": [
						"console",
						"verbose",
						"info"
					]
				}
			}
		})
		logging.captureWarnings(True)
		self.logger = logging.getLogger("bot.main")
		self.logger.info(f'Initialized at {self.init_time}.')

		self.lq = True
		self.stop_pings = False

		self.logger.info(f'Loading configs.')
		self.data = data.Data(self.rundir)

		self.logger.info(f'Loading cogs.')

		self.add_command(self.cog)

		for filename in os.listdir(f'{self.rundir}/python/cogs'):
			if filename.endswith('.py') and (not filename.endswith("disabled.py")):
				if gui if filename[:-3] == "gui" else filename[:-3] not in no_load:
					print("loading", filename, end="… ")
					t = time.perf_counter()
					self.load_extension(f'cogs.{filename[:-3]}')
					print(f"loaded. (took {time.perf_counter() - t:1.5f} seconds)")

		self.logger.info(f'Loading complete.')

	def run_bot(self, func, token_name=None):
		self.token = self.token or token_name
		if self.token not in self.data.tokens["discord"]:
			raise NameError(f"There's no token for bot account {self.token}, please check.")
		else:
			self.logger.info(f'Starting as {Fore.CYAN}{Style.BRIGHT}{self.token}{Style.NORMAL}{Fore.RESET} bot user')
		now = time.gmtime()
		self.start_time_ns = time.monotonic_ns()
		self.start_time = f'{now[0]}_{now[1]:02d}_{now[2]:02d}_{now[3]:02d}_{now[4]:02d}_{now[5]:02d}'
		self.logger.info(f"Started at {Style.BRIGHT}{Fore.YELLOW}{self.start_time}{Style.NORMAL}{Fore.RESET}")
		func(self.data.tokens["discord"].get(self.token))

	async def close(self):
		await self.change_presence(status=discord.Status.offline)
		await super(OmenaBot, self).close()

	async def close_bot(self, name="console", name_id=0):
		print("close_bot called")
		await self.close()
		self.logger.info(f'Bot Closed By {name} ID: {name_id}')
		print(f'Bot Closed By Developer: {name} ID: {name_id}')

	####################################
	# error catch area
	async def on_command_error(self, context: commands.Context, error):
		match error:
			case commands.NSFWChannelRequired():
				await context.send(f"Channel '{error.channel}' needs to be NSFW for this command to work.")

			case commands.MissingRequiredArgument():
				self.logger.info(f"{context.author} haven't filled all arguments. `{context.message.content}`")
				await context.send('Please fill all required arguments! :eyes:')

			case discord.errors.Forbidden():
				await context.send('Bot\'s missing permissions')

			case commands.MissingPermissions():
				self.logger.error(
					f"{context.author.name} (ID {context.author.id}) tried running command they don't have permission for.")
				await context.send("You're missing required permissions! :x:")
				print(
					f"{context.author.name} (ID {context.author.id}) tried running command they don't have permission for.")

			case commands.BotMissingPermissions(missing_permissions=perms, message=original):
				self.logger.critical("Bot is missing required permissions.")
				try:
					await context.send(f"{original[:-1]}! :x:")
				except discord.Forbidden:
					await context.author.send(f"{original[:-1]}! :x:\nIf you encounter this messsage but are not server stuff"
					                          f", please inform the server staff of it")

			case commands.CommandNotFound():
				self.logger.info(
					f'{context.message.author.name} (ID: {context.message.author.id}) tried to run command '
					f'"{context.invoked_with}" which does not exist.')
				await context.send(f'Command "{context.invoked_with}" does not exist! :x:')

			case commands.BadArgument():
				self.logger.info(f"{context.author} passed invalid arguments in arguments.")
				await context.send(f'Please check the arguments you provided\n{error.args}')
				await context.send("One of them couldn't be converted to {}".format(error.args[0].split('"')[1]))

			case commands.CommandError():
				import traceback

				[print(line) for line in traceback.format_exception(commands.CommandInvokeError, error, None)]
				self.logger.error(
					f"Unexpected error occured in command \"{context.command.name}\" with parameters {context.args[1:]}.")
				self.logger.error(error.message)
				await context.send(f"An unexpected error occured! :x:\n{error.message}")
