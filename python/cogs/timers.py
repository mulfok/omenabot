import asyncio
import inspect
import json
import logging
import random
import re
from math import sin, cos, tan, sqrt, asin, acos, atan, ceil, floor, pow, degrees as deg, radians as rad, pi

import discord
from discord.ext import commands, tasks
from discord.ext.commands import converter
from colorama import Fore, Style

from datetime import datetime

from omenabot import OmenaBot
from utils import misc


def setup(bot):
	bot.add_cog(Timers(bot))


class Timers(commands.Cog):

	@property
	def qualified_name(self):
		return "Timers"

	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.general")
		self.bot = bot
		self.running_timers = {}

	async def run_timer(self, time: datetime, guild_id: int, timer_id: int):
		name = self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]["name"]

		print(f'timer {guild_id}, "{Fore.CYAN}{Style.BRIGHT}{name}{Style.RESET_ALL}" {Fore.GREEN}running')
		time_left = time.timestamp() - datetime.now().timestamp()
		guild: discord.Guild = await self.bot.fetch_guild(guild_id)
		# await (guild.system_channel if guild.system_channel else guild.channels[0]).create_invite()
		ctx = await self.bot.fetch_channel(self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]["channel"])

		async def send_or_resend(content: str):
			if "message" in self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]:
				m = await ctx.fetch_message(int(self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]["message"]))
				await m.delete()
			message = await ctx.send(content)
			self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]["message"] = message.id
			self.bot.data.save_server(guild_id)
			with open(self.bot.data.prof_dir.joinpath(f'{guild_id}.json'), 'w') as prof_file:
				json.dump(self.bot.data.profiles[f'{guild_id}'], prof_file, indent=2)

		while time_left > 0:
			if time_left > 86400 * 7:
				await asyncio.sleep(time_left - 86400 * 7)
				await send_or_resend(f"one week left till **{name}**")
			elif time_left > 86400 * 3:
				await asyncio.sleep(time_left - 86400 * 3)
				await send_or_resend(f"three days left till **{name}**")
			elif time_left > 86400 * 2:
				await asyncio.sleep(time_left - 86400 * 2)
				await send_or_resend(f"two days left till **{name}**")
			elif time_left > 86400 * 1:
				await asyncio.sleep(time_left - 86400)
				await send_or_resend(f"one days left till **{name}**")
			elif time_left > 3600 * 12:
				await asyncio.sleep(time_left - 3600 * 12)
				await send_or_resend(f"twelve hours left till **{name}**")
			elif time_left > 3600 * 6:
				await asyncio.sleep(time_left - 3600 * 6)
				await send_or_resend(f"six hours left till **{name}**")
			elif time_left > 3600 * 3:
				await asyncio.sleep(time_left - 3600 * 3)
				await send_or_resend(f"three hours left till **{name}**")
			elif time_left > 3600 * 2:
				await asyncio.sleep(time_left - 3600 * 2)
				await send_or_resend(f"two hours left till **{name}**")
			elif time_left > 3600 * 1:
				await asyncio.sleep(time_left - 3600)
				await send_or_resend(f"ohe hour left till **{name}**")
			elif time_left > 60 * 30:
				await asyncio.sleep(time_left - 60 * 30)
				await send_or_resend(f"half an hour left till **{name}**")
			elif time_left > 60 * 15:
				await asyncio.sleep(time_left - 60 * 15)
				await send_or_resend(f"fifteen minutes left till **{name}**")
			elif time_left > 60 * 10:
				await asyncio.sleep(time_left - 60 * 10)
				await send_or_resend(f"ten minutes left till **{name}**")
			elif time_left > 60 * 5:
				await asyncio.sleep(time_left - 60 * 5)
				await send_or_resend(f"five minutes left till **{name}**")
			elif time_left > 60 * 3:
				await asyncio.sleep(time_left - 60 * 3)
				await send_or_resend(f"three minutes left till **{name}**")
			elif time_left > 60 * 1:
				await asyncio.sleep(time_left - 60)
				await send_or_resend(f"minute left till **{name}**")
			elif time_left > 30:
				await asyncio.sleep(time_left - 30)
				await send_or_resend(f"thirty seconds left till **{name}**")
			elif time_left > 15:
				await asyncio.sleep(time_left - 15)
				await send_or_resend(f"fifteen seconds left till **{name}**")
			elif time_left > 10:
				await asyncio.sleep(time_left - 10.1)
				await send_or_resend(f"ten")
			elif time_left > 5:
				await asyncio.sleep(time_left - 5.1)
				await send_or_resend(f"five")
			elif time_left > 4:
				await asyncio.sleep(time_left - 4.1)
				await send_or_resend(f"four")
			elif time_left > 3:
				await asyncio.sleep(time_left - 3.1)
				await send_or_resend(f"three")
			elif time_left > 2:
				await asyncio.sleep(time_left - 2.1)
				await send_or_resend(f"two")
			elif time_left > 1:
				await asyncio.sleep(time_left - 1.1)
				await send_or_resend(f"one")
			time_left = time.timestamp() - datetime.now().timestamp()
			pass
		await send_or_resend(f'Countdown **{name}** is done :congratulations:')
		await ctx.send("<@" + ">, <@".join(
			[str(r) for r in self.bot.data.profiles[f"{guild_id}"]["timers"][f"{timer_id}"]["notify"]]) + ">")
		self.bot.data.profiles[f'{guild_id}']["timers"].pop(f'{timer_id}')
		self.bot.data.save_server(guild_id)

	@commands.Cog.listener("on_ready")
	async def restart_tasks(self):
		subs = []
		# print(self.running_timers)
		for guild in self.bot.data.profiles:
			if "timers" in self.bot.data.profiles[guild]:
				timers = self.bot.data.profiles[guild]["timers"]
				keys = list(timers.keys())
				for timer_id in keys:
					if f"{guild}_{timer_id}" not in self.running_timers:
						print(
							f"timer {Style.BRIGHT}{timer_id}{Style.RESET_ALL} "
							f"for guild {Style.BRIGHT}{guild}{Style.RESET_ALL} is not running, starting"
						)
						timer = tasks.loop(count=1)(self.run_timer)
						# print(f"{guild}_{timer_id}")
						self.running_timers[f"{guild}_{timer_id}"] = timer
						time = datetime.fromtimestamp(self.bot.data.profiles[guild]["timers"][timer_id]["time"])
						subs += [timer.start(time, guild, timer_id)]
		await asyncio.gather(*subs)
		pass

	@commands.group("timers")
	async def root(self, context: commands.Context):
		print("it invoked")
		pass

	@root.command(name="countdown", aliases=["add", "timer"])
	async def countdown(self, context, name="timer", *time: str):
		time = ("2s",) if not time else time
		name = name.replace("_", " ")
		if f"{context.guild.id}" not in self.bot.data.profiles:
			self.bot.data.profiles[f'{context.guild.id}'] = {}
		if "timers" not in self.bot.data.profiles[f'{context.guild.id}']:
			self.bot.data.profiles[f'{context.guild.id}']["timers"] = {}
		time = misc.get_time(*time)
		timer_id = 0
		while f"{timer_id}" in self.bot.data.profiles[f'{context.guild.id}']["timers"]:
			timer_id += 1
		self.bot.data.profiles[f'{context.guild.id}']["timers"][f'{timer_id}'] = {
			"time": time.timestamp(),
			"name": name,
			"channel": context.channel.id,
			"notify": [context.author.id]
		}
		self.bot.data.save_server(context.guild.id)
		await context.send(f'countdown **{name}** happens at **{time.isoformat(" ")}**, waiting\n'
		                   f'<t:{int(time.timestamp())}:R>')
		timer = tasks.loop(count=1)(self.run_timer)
		self.running_timers[f"{context.guild.id}_{timer_id}"] = timer
		await timer.start(time, context.guild.id, timer_id)

	@root.command(name="list")
	async def list_timers(self, ctx: commands.Context):
		lines = []
		for timer_id in self.bot.data.profiles[f'{ctx.guild.id}']["timers"]:
			line = ""
			line += f"id: **{timer_id}** "
			line += f"name: **`{self.bot.data.profiles[f'{ctx.guild.id}']['timers'][timer_id]['name']}`** "
			line += f"ends at: <t:{int(self.bot.data.profiles[f'{ctx.guild.id}']['timers'][timer_id]['time'])}> or **<t:{int(self.bot.data.profiles[f'{ctx.guild.id}']['timers'][timer_id]['time'])}:R>**"
			lines += [line]
		await ctx.send("\n".join(lines))

	@root.command(name="rename")
	async def rename_timer(self, context: commands.Context, timer_id: str, *name: str):
		name = " ".join(name)
		orig = self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['name']
		self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['name'] = name
		self.bot.data.save_server(context.guild.id)
		await context.send(f"Renamed timer {orig} (id {timer_id}) to {name}")

	@root.command(name="remove")
	async def remove_timer(self, context: commands.Context, timer_id: str):
		await context.send("Are you sure?")
		res = None

		def check(m: discord.Message):
			locals()
			if (m.author, m.channel) == (context.author, context.channel):
				try:
					m.content = "." if misc.BoolConverter().convert(None, m.content) else ""
					return True
				except:
					return False
			else:
				return False
		if (await context.bot.wait_for('message', check=check)).content:
			orig = self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['name']
			self.bot.data.profiles[f'{context.guild.id}']['timers'].pop(timer_id)
			self.bot.data.save_server(context.guild.id)

			await context.send(f"Removed timer {orig} (id {timer_id})")
		else:
			await context.send("Removal canceled")

	@root.command(name="move")
	async def move_timer(self, context: commands.Context, timer_id: str, *time: str):
		time = ("2s",) if not time else time
		time = misc.get_time(*time)
		orig = self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['time']
		self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['time'] = time.timestamp()
		self.bot.data.save_server(context.guild.id)
		self.running_timers[f"{context.guild.id}_{timer_id}"].stop()
		del self.running_timers[f"{context.guild.id}_{timer_id}"]

		timer = tasks.loop(count=1)(self.run_timer)
		self.running_timers[f"{context.guild.id}_{timer_id}"] = timer
		await context.send(
			f"Moved timer {self.bot.data.profiles[f'{context.guild.id}']['timers'][timer_id]['name']} (id {timer_id}) from <t:{int(orig)}> to <t:{int(time)}> (or <t:{int(time)}:R>)")

		await timer.start(time, context.guild.id, timer_id)
