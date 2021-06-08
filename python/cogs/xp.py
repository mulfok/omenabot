import json
import logging
import math
import os
import typing

import discord
import regex
from discord.ext import commands

from omenabot import OmenaBot


class Xp(commands.Cog):
	profiles = {}

	bot: OmenaBot

	@property
	def qualified_name(self):
		return "xp system"

	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.general")
		self.bot = bot
		self.prof_dir = bot.rundir.joinpath('private', 'profiles')
		if not os.path.exists(self.prof_dir):
			os.mkdir(self.prof_dir)
		for file in os.listdir(self.prof_dir):
			with open(self.prof_dir.joinpath(file)) as prof_file:
				self.profiles[file[0:-5]] = json.load(prof_file)

	@staticmethod
	def calculate_level(xp: typing.SupportsFloat) -> float:
		return math.log((xp / 10.) + 1, 1.3) + 1

	@staticmethod
	def calculate_next_level(current_level: int) -> int:
		return math.ceil(10 * (pow(1.3, current_level) - 1))

	@staticmethod
	def calculate_xp(message: discord.Message) -> int:
		contents: str = message.clean_content
		contents = '﻿﻿'.join(regex.split(":[^:]+:", contents))
		text_n_code = contents.split("```")
		text = []
		for i in range(len(text_n_code)):
			if i % 2 == 0:
				text += [text_n_code[i]]
		contents = " some code ".join(text)
		words_and_nums = regex.findall("[\p{L}'-]+|[0-9]+\\.[0-9]+|\\.?[0-9]+\\.?", contents)
		if len(words_and_nums) > 4:
			# print(words_and_nums)
			return math.floor(len(contents) * math.log(len(words_and_nums), 3))
		else:
			return 0

	@commands.Cog.listener("on_message")
	async def on_message(self, message: discord.Message):  # ﻿
		ctx: commands.Context = await self.bot.get_context(message)
		if ctx and ctx.valid or message.author.bot:
			return
		if f'{message.guild.id}' not in self.profiles:
			self.profiles[f'{message.guild.id}'] = {}
		server = self.profiles[f'{message.guild.id}']
		if f'{message.author.id}' not in server:
			server[f'{message.author.id}'] = {}
		if 'xp' not in server[f'{message.author.id}']:
			server[f'{message.author.id}']['xp'] = 0
			server[f'{message.author.id}']['lvl'] = 0
		xp = self.calculate_xp(message)
		server[f'{message.author.id}']['xp'] += xp
		server[f'{message.author.id}']['lvl'] = self.calculate_level(server[f'{message.author.id}']['xp'])
		self.profiles[f'{message.guild.id}'] = server
		with open(self.prof_dir.joinpath(f'{message.guild.id}.json'), 'w') as prof_file:
			json.dump(server, prof_file, indent=2)

	@commands.Cog.listener(name="on_message_edit")
	async def message_edited(self, before: discord.Message, after: discord.Message):
		xp_before = self.calculate_xp(before)
		xp_after = self.calculate_xp(after)
		if f'{after.guild.id}' not in self.profiles:
			self.profiles[f'{after.guild.id}'] = {}
		server = self.profiles[f'{after.guild.id}']
		if f'{after.author.id}' not in server:
			server[f'{after.author.id}'] = {}
		if 'xp' not in server[f'{after.author.id}']:
			server[f'{after.author.id}']['xp'] = 0
			server[f'{after.author.id}']['lvl'] = 0
		server[f'{after.author.id}']['xp'] += xp_after - xp_before
		server[f'{after.author.id}']['lvl'] = self.calculate_level(server[f'{after.author.id}']['xp'])
		self.profiles[f'{after.guild.id}'] = server
		with open(self.prof_dir.joinpath(f'{after.guild.id}.json'), 'w') as prof_file:
			json.dump(server, prof_file, indent=2)

	@commands.Cog.listener("on_raw_reaction_add")
	async def raw_check_xp(self, payload: discord.RawReactionActionEvent):
		guild: discord.Guild = self.bot.get_guild(payload.guild_id)
		if guild:
			channel: discord.TextChannel = guild.get_channel(payload.channel_id)
			if channel and isinstance(channel, discord.TextChannel):
				message = await channel.fetch_message(payload.message_id)
				if not payload.emoji.id and payload.event_type == "REACTION_ADD" and payload.emoji.name == '👥':
					embed = discord.Embed()
					embed.set_author(name=message.author.display_name, url=f"https://discordapp.com/channels/@me/{message.author.id}", icon_url=message.author.avatar_url)
					embed.add_field(name="xp", value=self.calculate_xp(message))
					embed.add_field(name="message", value=f"[jump]({message.jump_url})")
					await message.remove_reaction(payload.emoji, payload.member)
					await payload.member.send("", embed=embed)

	@commands.Cog.listener("on_reaction_add")
	async def check_xp(self, reaction: discord.Reaction, user: discord.User):
		if not reaction.custom_emoji and reaction.emoji == '👥':
			message: discord.Message = reaction.message
			embed = discord.Embed()
			embed.set_author(name=message.author.display_name, url=f"https://discordapp.com/channels/@me/{message.author.id}", icon_url=message.author.avatar_url)
			embed.add_field(name="xp", value=self.calculate_xp(message))
			embed.add_field(name="message", value=f"[jump]({message.jump_url})")
			await reaction.remove(user)
			await user.send("", embed=embed)

	@commands.command(name='xp', aliases=['level'])
	async def get_xp(self, ctx: commands.Context):
		if f'{ctx.guild.id}' not in self.profiles:
			self.profiles[f'{ctx.guild.id}'] = {}
		if f'{ctx.author.id}' not in self.profiles[f'{ctx.guild.id}']:
			self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}'] = {}
		if 'xp' not in self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}']:
			self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}']['xp'] = 0
			self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}']['lvl'] = 0
		current_xp = self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}']['xp']
		current_level = self.profiles[f'{ctx.guild.id}'][f'{ctx.author.id}']['lvl']
		embed = discord.Embed()
		embed.set_author(name=f'Xp of "{ctx.author.name}"')
		embed.set_thumbnail(url=ctx.author.avatar_url)
		embed.colour = 0xff
		embed.add_field(name="XP", value=current_xp)
		embed.add_field(name="Level", value=math.floor(current_level))
		next_level_xp = self.calculate_next_level(math.floor(current_level))
		current_level_xp = self.calculate_next_level(math.floor(current_level) - 1)
		embed.add_field(name="Xp to next level", value=next_level_xp - current_xp)
		embed.add_field(name="Current level progress",
						value=f"{(current_xp - current_level_xp) / (next_level_xp - current_level_xp) * 100:<1.3f}%")
		await ctx.send("", embed=embed)

	@commands.command(name="give_xp", hidden=True)
	async def manage_xp(self, ctx: commands.Context, user: discord.Member, amount: int):
		await ctx.message.delete()
		gid = f'{ctx.guild.id}'
		aid = f'{ctx.author.id}'
		if aid in self.bot.config['devs']:
			aid = f'{user.id}'
			if gid not in self.profiles:
				self.profiles[gid] = {}
			if f'{ctx.author.id}' not in self.profiles[gid]:
				self.profiles[gid][aid] = {}
			if 'xp' not in self.profiles[gid][aid]:
				self.profiles[gid][aid]['xp'] = amount
				self.profiles[gid][aid]['lvl'] = self.calculate_level(amount)
			else:
				self.profiles[gid][aid]['xp'] += amount
				self.profiles[gid][aid]['lvl'] = self.calculate_level(self.profiles[gid][aid]['xp'])
			with open(self.prof_dir.joinpath(f'{gid}.json'), 'w') as prof_file:
				json.dump(self.profiles[gid], prof_file, indent=2)

	@commands.command(name="xptop", aliases=["top", "levels", "leveltop"])
	async def get_top(self, ctx: commands.Context):
		if f'{ctx.guild.id}' not in self.profiles:
			self.profiles[f'{ctx.guild.id}'] = {}
		levels = [(
			ctx.guild.get_member(int(id)).name if not ctx.guild.get_member(int(id)).nick else ctx.guild.get_member(
				int(id)).name,
			self.profiles[f'{ctx.guild.id}'][id]['xp'],
			math.floor(self.profiles[f'{ctx.guild.id}'][id]['lvl'])
		) for id in self.profiles[f'{ctx.guild.id}'].keys()]
		levels.sort(key=lambda l: l[1], reverse=True)
		embed = discord.Embed()
		embed.set_author(name='levels')
		for l in levels:
			embed.add_field(name=l[0], value=f'xp: {l[1]}; level: {l[2]}')
		await ctx.send("", embed=embed)

	@commands.command(name="update_xp", hidden=True)
	async def update_xp_curve(self, ctx: commands.Context):
		await self.bot.http.delete_message(ctx.channel.id, ctx.message.id, reason="xp update command")
		for id in self.profiles[f'{ctx.guild.id}']:
			self.profiles[f'{ctx.guild.id}'][id]['lvl'] = self.calculate_level(
				self.profiles[f'{ctx.guild.id}'][id]['xp'])
		with open(self.prof_dir.joinpath(f'{ctx.guild.id}.json'), 'w') as prof_file:
			json.dump(self.profiles[f'{ctx.guild.id}'], prof_file, indent=2)


def setup(bot):
	bot.add_cog(Xp(bot))
