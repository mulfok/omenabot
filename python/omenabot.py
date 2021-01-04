import json
import logging
import os
import pathlib
import random
import sys
import time
from itertools import cycle

import discord
from colorama import Fore, Style, init as init_terminal_styling
from discord.ext import commands, tasks


# List comprehesions: wanted_roles = [i[7:] for i in message.content.split("\n")]
# Lambdas: wanted_roles = list(map(lambda i: i[7:], message.content.split("\n")))
class OmenaBot(commands.bot.Bot):

	def command(name=None, cls=None, **attrs):
		if cls is None:
			cls = commands.Command

		def decorator(func):
			if isinstance(func, commands.Command):
				raise TypeError('Callback is already a command.')
			return cls(func, name=name, **attrs)

		return decorator

	@staticmethod
	def parse_duration(duration: int):
		minutes, seconds = divmod(duration, 60)
		hours, minutes = divmod(minutes, 60)
		days, hours = divmod(hours, 24)
		weeks, wdays = divmod(days, 7)
		months, mdays = divmod(days, 30)
		years, ydays = divmod(days, 365)

		duration = []
		if years > 0:
			duration.append(f'{years} days')
			if ydays > 0:
				duration.append(f'{ydays} days')
		elif months > 0:
			duration.append(f'{months} days')
			if mdays > 0:
				duration.append(f'{mdays} days')
		elif weeks > 0:
			duration.append(f'{weeks} days')
			if wdays > 0:
				duration.append(f'{wdays} days')
		elif days > 0:
			duration.append(f'{days} days')
		if hours > 0:
			duration.append(f'{hours} hours')
		if minutes > 0:
			duration.append(f'{minutes} minutes')
		if seconds > 0:
			duration.append(f'{seconds} seconds')

		return ', '.join(duration)

	# grabs server prefix from each server
	async def get_prefix(self, message: discord.Message):
		"""

		:param message:
		:return: prefix for :param client: in :param message:
		"""
		if message.channel.type.value == 1:
			return '.'
		if not self.servers[str(message.guild.id)].get('prefix'):
			return '~'
		else:
			return self.servers[str(message.guild.id)].get('prefix')

	status = cycle(['help - Brings up commands', 'aboutme - Shows bot info', 'trivia - Fun facts!',
									'changeprefix - Customise server prefix!', 'Ping me to get prefix on the server'])

	# Various debug console message events
	async def on_connect(self):
		self.logger.info('Connected to discord...')

	async def on_disconnect(self):
		self.logger.info('Disconnected from discord.')

	async def on_ready(self):
		# set status, change activity and print ready and start loop
		self.change_status.start()
		# hail_theOwner.start()
		await self.change_presence(status=discord.Status.online, activity=discord.Game('~helpme for commands!'))
		self.logger.info(f'Logged in as {self.user.name}')
		self.logger.info(f'Client ID: {self.user.id}')
		self.logger.info('---------')
		print(f"{Fore.GREEN}Ready")

	# Set default command prefix on server join
	async def on_guild_join(self, guild):
		self.logger.info(f'Bot joined {guild.name} (ID: {guild.id})')
		print(f'{Fore.MAGENTA}Bot has joined {guild.name} (ID: {guild.id})!')
		with open(f'{self.rundir}/private/servers.json', 'r') as server_file:
			servers = json.load(server_file)

		servers[str(guild.id)] = {}
		servers[str(guild.id)]["prefix"] = '~'

		with open(f'{self.rundir}/private/servers.json', 'w') as server_file:
			json.dump(servers, server_file, indent=2)

	# Purge command prefix upon server leave
	async def on_guild_remove(self, guild):
		self.logger.info(f'Bot left {guild.name} (ID: {guild.id})')
		with open(f'{self.rundir}/private/servers.json', 'r') as server_file:
			self.servers = json.load(server_file)

		self.servers.pop(str(guild.id))

		with open(f'{self.rundir}/private/servers.json', 'w') as server_file:
			json.dump(self.servers, server_file, indent=2)

	@staticmethod
	def roll_one(dice: int):
		return random.randrange(dice) + 1

	@staticmethod
	def roll(dices: int, dice: int, keep: int):
		rolls = [OmenaBot.roll_one(dice) for _ in range(dices)]
		rolls.sort()
		rolls = rolls[len(rolls) - keep:]
		return rolls

	@staticmethod
	def get_stat():
		rolled = OmenaBot.roll(4, 6, 3)
		stat = 0
		for i in range(3):
			stat += rolled[i]
		return f"{stat}({int((stat + 1) / 2) - 5})"

	async def on_member_join(self, member: discord.Member):
		if self.servers[f'{member.guild.id}'].get('name') is None:
			self.servers[f'{member.guild.id}']['name'] = member.guild.name
		if member.guild.id == 663903542842490910:
			print(f"{Fore.MAGENTA}{member} joined testman")
		else:
			self.logger.info(f'{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')
			print(f'{Fore.GREEN}{member} (ID: {member.id}) has joined {member.guild.name} (ID: {member.guild.id})!')

	async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
		if not member_before.nick == member_after.nick:
			if not self.servers.get(f'{member_after.guild.id}') is None:
				if not self.servers[f'{member_after.guild.id}'].get("nicks") is None:
					if f'{member_after.id}' in self.servers[f'{member_after.guild.id}']["nicks"]:
						if not self.servers[f'{member_after.guild.id}']["nicks"][f'{member_after.id}'] == member_after.nick:
							print(f'member changed nick to {member_before.nick} while having '
										f'permanick {self.servers[f"{member_after.guild.id}"]["nicks"][f"{member_after.id}"]}')
							await member_after.edit(reason="permanent nickname",
																			nick=self.servers[f'{member_after.guild.id}']["nicks"][f'{member_after.id}'])

	async def on_member_remove(self, member: discord.Member):
		if self.servers[f'{member.guild.id}'].get('name') is None:
			self.servers[f'{member.guild.id}']['name'] = member.guild.name
		if member.guild.id == 663903542842490910:
			print(f"{Fore.MAGENTA}{member} left testman")
			print(member.guild.system_channel())
		else:
			self.logger.info(f'{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')
			print(f'{Fore.RED}{member} (ID: {member.id}) has left {member.guild.name} (ID: {member.guild.id})!')

	# Tasks Area
	@tasks.loop(seconds=5)
	async def change_status(self):
		await self.change_presence(activity=discord.Game(next(self.status)))

	async def on_message(self, message: discord.Message):
		if not message.author == self.user:
			if message.channel.type.name == 'private':
				if not message.author.bot and message.content:
					ctx = await self.get_context(message)
					await self.invoke(ctx)
					if not ctx.command == "close":
						await message.channel.send(
							"I'm a bot, and certanly not smart enough to talk to you, my friend ¯\\_(°^°)\\_/¯", delete_after=2)
			else:
				if self.servers.get(f'{message.guild.id}') is None:
					self.servers[f'{message.guild.id}'] = {}
					self.servers[f'{message.guild.id}']['name'] = message.guild.name
					with open(f'{self.rundir}/private/servers.json', 'w') as server_file:
						json.dump(self.servers, server_file, indent=2)
				if self.servers[f'{message.guild.id}'].get("name") is None:
					self.servers[f'{message.guild.id}']['name'] = message.guild.name
					with open(f'{self.rundir}/private/servers.json', 'w') as server_file:
						json.dump(self.servers, server_file, indent=2)
				if not self.servers[f'{message.guild.id}']["name"] == message.guild.name:
					self.servers[f'{message.guild.id}']['name'] = message.guild.name
					with open(f'{self.rundir}/private/servers.json', 'w') as server_file:
						json.dump(self.servers, server_file, indent=2)
				channels = self.servers[f'{message.guild.id}'].get('channels')
				if channels is not None:
					image_only = channels.get('image-only')
					if image_only is not None:
						if message.channel.permissions_for(message.guild.get_member(self.user.id)).manage_messages:
							if (message.channel.id in image_only) if isinstance(image_only, list) else (
											message.channel.id == image_only):
								if not message.attachments:
									ctx = await self.get_context(message)
									if not ctx.command:
										commands_cog = self.get_cog("General")
										if commands_cog:
											await commands_cog.clear(ctx, 0)
										else:
											await message.delete()
										return
				if not message.content.startswith(".."):
					await self.process_commands(message)
				if message.content[0:22] == f"<@!{self.user.id}>":
					if message.content[23:] == "guilds":
						await message.delete()
						guilds = ""
						for guild in self.guilds:
							guilds = "\n".join([guilds, guild.name + f' (ID: {guild.id})'])
						await message.author.send(f"Currently i'm in {len(self.guilds)}, which are ```fix\n{guilds}\n```")
					else:
						await message.delete()
						self.logger.info(f"Bot was pinged in {message.guild.id}, by {message.author.id}")
						await message.channel.send(f'Current prefix is "`{await self.get_prefix(message)}`"')

	####################################
	# error catch area
	async def on_command_error(self, ctx: commands.context, error):
		# checks to see if command is missing args, then sends message
		if isinstance(error, commands.MissingRequiredArgument):
			self.logger.info(f"{ctx.author} haven't filled all arguments. `{ctx.message.content}`")
			await ctx.send('Please fill all required arguments! :eyes:')
			return

		if isinstance(error, discord.errors.Forbidden):
			await ctx.send('Bot\'s missing permissions')
			return

		# checks to see if permissions all exist
		if isinstance(error, commands.MissingPermissions):
			self.logger.error(f"{ctx.author.name} (ID {ctx.author.id}) tried running command they don't have permission to.")
			await ctx.send("You're missing required permissions! :x:")
			print("Someone tried to run a command that they don't have permissions for!")
			return

		# checks to see if command args being passed in are invalid/unparseable, then sends message
		if isinstance(error, commands.BadArgument):
			self.logger.info(f"{ctx.author} passed invalid arguments in arguments.")
			await ctx.send(f'Please check the arguments you provided\n{error.args[1]}')
			await ctx.send("One of them couldn't be converted to {}".format(error.args[0].split('"')[1]))
			return

		if isinstance(error, commands.BotMissingPermissions):
			self.logger.critical("Bot is missing required permissions.")
			await ctx.send("I'm missing administrator permissions! :x:")
			return

		if isinstance(error, commands.CommandNotFound):
			self.logger.info(
				f'{ctx.message.author.name} (ID: {ctx.message.author.id}) tried to run command '
				f'"{ctx.invoked_with}" which does not exist.')
			await ctx.send(f'Command "{ctx.invoked_with}" does not exist! :x:')
			return

		import traceback
		[print(line) for line in traceback.format_exception(commands.CommandInvokeError, error, None)]
		self.logger.error(f"Unexpected error occured in command \"{ctx.command.name}\" with parameters {ctx.args[1:]}.")
		self.logger.error(error.original)
		await ctx.send("An unexpected error occured! :x:")

	# -----------------------------------
	# Cogs Load
	@commands.command(hidden=True)
	async def load(self, ctx, extension):
		print(ctx, extension)
		self.load_extension(f'cogs.{extension}')

	# Cogs Unload
	@commands.command(hidden=True)
	async def unload(self, ctx, extension):
		self.unload_extension(f'cogs.{extension}')

	def __init__(self, **options):
		super().__init__(self.get_prefix, **options)

		self.start_time_ns: int = 0
		self.start_time = ""
		self.output = None
		init_terminal_styling(autoreset=True)
		now = time.gmtime()
		self.init_time_ns = time.monotonic_ns()
		self.init_time = f'{now[0]}_{str(now[1]).rjust(2, "0")}_{str(now[2]).rjust(2, "0")}_{str(now[3]).rjust(2, "0")}_{str(now[4]).rjust(2, "0")}_{str(now[5]).rjust(2, "0")}'
		print(f"Initialized at {Style.BRIGHT}{Fore.YELLOW}{self.init_time}")

		self.rundir = pathlib.Path(__file__, ).parent.parent.absolute()
		self.home = os.getenv('HOME')

		try:
			stats = os.stat(f"{self.rundir}/python/logs/latest.log")
			created = time.gmtime(stats.st_ctime)
			created_time = f'{created[0]}_{str(created[1]).rjust(2, "0")}_{str(created[2]).rjust(2, "0")}_{str(created[3]).rjust(2, "0")}_{str(created[4]).rjust(2, "0")}_{str(created[5]).rjust(2, "0")}'
			os.rename(f"{self.rundir}/python/logs/latest.log", f"{self.rundir}/python/logs/{created_time}.log")
		except FileNotFoundError:
			print(f"{Style.DIM}No latest log.")
		logging.basicConfig(format="[%(asctime)s] [%(threadName)s|%(name)s/%(levelname)-5s] %(message)s", filename=f'{self.rundir}/python/logs/latest.log', level=logging.INFO)
		self.logger = logging.getLogger("bot.main")
		self.logger.info(f'Initialized at {self.init_time}.')

		self.lq = True
		self.stop_pings = False

		self.logger.info(f'Loading configs.')

		with open(f'{self.rundir}/private/servers.json') as servers_file:
			self.servers = json.load(servers_file)

		with open(f'{self.rundir}/private/dnd.json') as servers_file:
			self.dnd_conf = json.load(servers_file)

		with open(f'{self.rundir}/private/bot.json') as file:
			self.config = json.load(file)

		with open(f"{self.rundir}/responselists.json") as file:
			self.responses = json.load(file)

		self.logger.info(f'Loading cogs.')

		for filename in os.listdir(f'{self.rundir}/cogs'):
			if filename.endswith('.py'):
				print(filename)
				if not filename.startswith("gui") or "-gui" in sys.argv:
					self.load_extension(f'cogs.{filename[:-3]}')

		self.logger.info(f'Loading complete.')
		print("Loading complete.")

	def run_bot(self, func, *args, **kwargs):
		now = time.gmtime()
		self.start_time_ns = time.monotonic_ns()
		self.start_time = f'{now[0]}_{now[1]}_{now[2]}_{now[3]}_{now[4]}_{now[5]}'
		print(f"Started at {Style.BRIGHT}{Fore.YELLOW}{self.start_time}")
		func(*args, **kwargs)

	async def close_bot(self, name="console", name_id=0):
		print("close_bot called")
		await self.close()
		self.logger.info(f'Bot Closed By {name} ID: {name_id}')
		print(f'Bot Closed By Developer: {name} ID: {name_id}')
