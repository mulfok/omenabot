import json
import logging
import math
import numbers
import numpy

import discord
import regex
from discord.ext import commands

from omenabot import OmenaBot
from utils import misc


class Xp(commands.Cog):
	bot: OmenaBot

	@property
	def qualified_name(self):
		return "xp system"

	async def cog_check(self, context: commands.Context, **kwargs):
		chan: discord.TextChannel = context.channel
		perms: discord.Permissions = chan.permissions_for(context.guild.get_member(self.bot.user.id))
		return perms.embed_links and perms.send_messages

	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.general")
		self.bot = bot

	@staticmethod
	def calculate_level(xp: float) -> float:
		return math.log((xp / 10.) + 1, 1.3) + 1

	@staticmethod
	def calculate_next_level(current_level: int) -> int:
		return math.ceil(10 * (pow(1.3, current_level) - 1))

	@staticmethod
	def calculate_xp(message: discord.Message) -> int:
		# noinspection PyTypeChecker
		contents: str = message.clean_content
		contents = '﻿emoji﻿'.join(regex.split(":[^:]+:", contents))
		text_n_code = contents.split("```")
		text = []
		for i in range(0, len(text_n_code), 2):
			text += [text_n_code[i]]
		contents = " some code ".join(text)
		words_and_nums = regex.findall("[\\p{L}'-]+|[0-9]+\\.[0-9]+|\\.?[0-9]+\\.?", contents)
		if len(words_and_nums) > 4:
			# print(words_and_nums)
			return math.floor(len(contents) * math.log(len(words_and_nums), 3))
		else:
			return 0

	@commands.Cog.listener("on_message")
	async def on_message(self, message: discord.Message):  # ﻿
		context: commands.Context = await self.bot.get_context(message)
		if (context and context.valid) or (not message) or message.author.bot or not message.guild:
			return
		user = self.bot.data.profiles.setdefault(f'{message.guild.id}', {}).setdefault("users", {}).setdefault(f'{message.author.id}', {})
		user['xp'] = user.setdefault('xp', 0) + self.calculate_xp(message)
		user['lvl'] = self.calculate_level(user['xp'])
		self.bot.data.save_server(message.guild.id)

	@commands.Cog.listener(name="on_message_edit")
	async def message_edited(self, before: discord.Message, after: discord.Message):
		context: commands.Context = await self.bot.get_context(after)
		if (context and context.valid) or (not after) or after.author.bot or not after.guild:
			return
		user = self.bot.data.profiles.setdefault(f'{after.guild.id}', {}).setdefault("users", {}).setdefault(f'{after.author.id}', {})
		user['xp'] = user.setdefault('xp', 0) + self.calculate_xp(after) - self.calculate_xp(before)
		user['lvl'] = self.calculate_level(user['xp'])
		self.bot.data.save_server(after.guild.id)

	@commands.Cog.listener("on_raw_reaction_add")
	async def raw_check_xp(self, payload: discord.RawReactionActionEvent):
		guild: discord.Guild = self.bot.get_guild(payload.guild_id)
		if guild:
			channel: discord.TextChannel = guild.get_channel(payload.channel_id)
			if channel and isinstance(channel, discord.TextChannel):
				message = await channel.fetch_message(payload.message_id)
				if not payload.emoji.id and payload.event_type == "REACTION_ADD" and payload.emoji.name == '👥':
					embed = discord.Embed()
					embed.set_author(
						name=message.author.display_name,
						url=f"https://discord.com/channels/@me/{message.author.id}",
						icon_url=message.author.avatar.url)
					embed.add_field(name="xp", value=str(self.calculate_xp(message)))
					embed.add_field(name="message", value=f"[jump]({message.jump_url})")
					await message.remove_reaction(payload.emoji, payload.member)
					await payload.member.send("", embed=embed)

	@commands.command(name='xp', aliases=['level', "lv"])
	async def get_xp(self, context: commands.Context, mention: str = None):
		member = misc.find_member(context.message, mention) if mention else context.author
		if not member:
			await context.send(f'could not find member for mention "{mention}"')
			return
		current_xp = self.bot.data.profiles.setdefault(f'{context.guild.id}', {}).setdefault("users", {}).setdefault(f"{member.id}", {}).setdefault("xp", 0)
		current_level = self.bot.data.profiles[f'{context.guild.id}']["users"][f'{member.id}'].setdefault('lvl', 0)
		embed = discord.Embed()
		embed.set_author(name=f'Xp of "{member.name}"')
		embed.set_thumbnail(url=member.avatar.url)
		embed.colour = 0xff
		embed.add_field(name="XP", value=current_xp)
		embed.add_field(name="Level", value=str(math.floor(current_level)))
		try:
			next_level_xp = self.calculate_next_level(math.floor(current_level))
		except OverflowError:
			embed.add_field(name="Xp to next level", value=float("nan"))
			embed.add_field(
				name="Current level progress",
				value="?"
			)
		else:
			current_level_xp = self.calculate_next_level(math.floor(current_level) - 1)
			embed.add_field(name="Xp to next level", value=next_level_xp - current_xp)
			embed.add_field(
				name="Current level progress",
				value=f"{(current_xp - current_level_xp) / (next_level_xp - current_level_xp) * 100:<1.3f}%"
			)
		if not context.author.id == member.id:
			embed.set_footer(text=f'Requested by {context.author.display_name}', icon_url=context.author.avatar.url)
		await context.send("", embed=embed)

	@commands.command(name="manage-xp", hidden=True)
	async def manage_xp(self, context: commands.Context, user, *amount: str):
		await context.message.delete()
		gid = f'{context.guild.id}'
		aid = f'{context.author.id}'
		user = misc.find_member(context.message, user)
		if aid in self.bot.data.bot['devs'] and user:
			aid = f'{user.id}'
			self.bot.data.profiles.setdefault(gid, {}).setdefault("users", {}).setdefault(aid, {})
			if "set" in amount:
				if "level" in amount:
					xp = self.calculate_next_level(int(amount[-1]) - 1)
				else:
					xp = int(amount[-1])
				self.bot.data.profiles[gid]["users"][aid]['xp'] = xp
			else:
				if "level" in amount:
					if "xp" in self.bot.data.profiles[gid]["users"][aid]:
						current_level = self.bot.data.profiles[f'{context.guild.id}']["users"][aid]['lvl']
						current_level_xp = self.calculate_next_level(math.floor(current_level) - 1)
						level_xp = self.bot.data.profiles[gid]["users"][aid]['xp'] - current_level_xp
						self.bot.data.profiles[gid]["users"][aid]['xp'] = self.calculate_next_level(
							math.floor(current_level) - 1 + int(amount[-1])
						) + level_xp
				else:
					if 'xp' not in self.bot.data.profiles[gid]["users"][aid]:
						self.bot.data.profiles[gid]["users"][aid]['xp'] = int(amount[-1])
					else:
						self.bot.data.profiles[gid]["users"][aid]['xp'] += int(amount[-1])
			self.bot.data.profiles[gid]["users"][aid]['lvl'] = self.calculate_level(self.bot.data.profiles[gid]["users"][aid]['xp'])
			self.bot.data.save_server(context.guild.id)

	@commands.command(name="xptop", aliases=["levels", "leveltop"])
	async def get_top(self, context: commands.Context):
		members = self.bot.data.profiles.setdefault(f'{context.guild.id}', {}).setdefault("users", {}).keys()
		to_show = []
		for member in members:
			try:
				if not context.guild.get_member(int(member)):
					await context.guild.fetch_member(int(member))
				if self.bot.data.profiles[f'{context.guild.id}']["users"][member]['xp'] > 0:
					to_show += [member]
			except discord.errors.NotFound:
				pass
		levels = [(
			context.guild.get_member(int(member)).display_name,
			self.bot.data.profiles[f'{context.guild.id}']["users"][member]['xp'],
			math.floor(self.bot.data.profiles[f'{context.guild.id}']["users"][member]['lvl'])
		) for member in to_show if context.guild.get_member(int(member))]
		levels.sort(key=lambda l: l[1], reverse=True)
		embed = discord.Embed()
		embed.set_author(name='levels')
		for level in levels:
			embed.add_field(name=level[0], value=f'xp: {level[1]}; level: {level[2]}')
		await context.send("", embed=embed)

	@commands.command(name="update_xp", hidden=True)
	async def update_xp_curve(self, context: commands.Context):
		await self.bot.http.delete_message(context.channel.id, context.message.id, reason="xp update command")
		for member in self.bot.data.profiles[f'{context.guild.id}']["users"]:
			self.bot.data.profiles[f'{context.guild.id}']["users"][member]['lvl'] = self.calculate_level(
				self.bot.data.profiles[f'{context.guild.id}']["users"][member]['xp']
			)
		self.bot.data.profiles[f'{context.guild.id}']["users"] = {
			k: self.bot.data.profiles[f'{context.guild.id}']["users"][k] for k in sorted(
				self.bot.data.profiles[f'{context.guild.id}']["users"].keys()
			)
		}
		self.bot.data.save_server(context.guild.id)


def setup(bot):
	bot.add_cog(Xp(bot))
