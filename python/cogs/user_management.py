import json
import logging

import discord
from discord.ext import commands

from omenabot import OmenaBot
from utils import misc


class UserManagement(commands.Cog):
	"""User management
	user management module, kick, ban, unban etc.
	"""

	@property
	def qualified_name(self):
		return "User management"

	def __init__(self, bot: OmenaBot):
		self.logger = logging.getLogger("bot.user management")
		self.bot = bot
		self.logger.info("User Management module started")

	@commands.command()
	# set params and kick
	async def kick(self, ctx: commands.Context, member: str, *, reason=None):
		perms: discord.Permissions = ctx.message.author.permissions_in(ctx.channel)
		member = misc.find_member(ctx.message, member)
		if perms.kick_members or f"{ctx.author.id}" in self.bot.data.bot["devs"]:
			self.logger.critical(
				f'{member.mention} (ID {member.id}) was kicked from server {ctx.guild.id} with reason: "{reason}".')
			await member.kick(reason=reason)
			await ctx.send(f'{member.mention} was kicked from the server. :hammer:')
		else:
			commands.MissingPermissions(perms.kick_members)

	@commands.command()
	@commands.has_permissions(administrator=True)
	# set params and BAN
	async def ban(self, ctx: commands.Context, member: str, *, reason=None):
		perms: discord.Permissions = ctx.message.author.permissions_in(ctx.channel)
		if perms.ban_members or f"{ctx.author.id}" in self.bot.data.bot["devs"]:
			member = misc.find_member(ctx.message, member)
			self.logger.critical(
				f'{member.mention} (ID {member.id}) was banned from server {ctx.guild.id} with reason: "{reason}".')
			await member.ban(reason=reason)
			await ctx.send(f'{member.mention} was banned from the server. :hammer:')
		else:
			commands.MissingPermissions(perms.ban_members)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unban(self, ctx: commands.Context, *, member):
		perms: discord.Permissions = ctx.message.author.permissions_in(ctx.channel)
		if perms.ban_members or f"{ctx.author.id}" in self.bot.data.bot["devs"]:
			# grab server ban list and return
			banned_users: list[discord.guild.BanEntry] = await ctx.guild.bans()
			member_name, member_discriminator = member.split('#')

			for ban_entry in banned_users:
				user = ban_entry.user

				if (user.name, user.discriminator) == (member_name, member_discriminator):
					self.logger.critical(f'{member.mention} (ID {member.id}) was unbanned from server {ctx.guild.id}.')
					await ctx.guild.unban(user)
					await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
					return
		else:
			commands.MissingPermissions(perms.ban_members)

	@commands.command()
	async def setnick(self, ctx: commands.Context, *value: str):
		if not (
						ctx.author.guild_permissions.manage_nicknames or
						ctx.author.guild_permissions.administrator or
						self.bot.data.bot["devs"].get(f"{ctx.author.id}")
		):
			raise commands.MissingPermissions(discord.permissions.Permissions(permissions=1 << 27))
		print(value)
		member = misc.find_member(ctx.message, value[0])
		await ctx.message.delete()
		if 'nicks_pre' not in self.bot.data.profiles[f'{ctx.guild.id}']:
			self.bot.data.profiles[f'{ctx.guild.id}']["nicks_pre"] = {}
		while isinstance(value, tuple) and isinstance(value[0], tuple):
			value = value[0]
		if len(value) < 2:
			if not self.bot.data.profiles[f'{ctx.guild.id}'].setdefault("nicks", {}).get(f'{member.id}') is None:
				self.bot.data.profiles[f'{ctx.guild.id}']["nicks"].pop(f'{member.id}')
				await ctx.send(f"reset permanent nick for {member}", delete_after=3)
				await member.edit(nick=self.bot.data.profiles[f'{ctx.guild.id}'].setdefault("nicks_pre", {}).pop(f'{member.id}'))
		else:
			permanentnick = ' '.join(value[1:])
			if len(permanentnick) > 32:
				await ctx.send(f"Nickname `{permanentnick}` is too long (32 characters max).", delete_after=7)
				return
			self.bot.data.profiles[f'{ctx.guild.id}'].setdefault("nicks", {})[f'{member.id}'] = permanentnick
			if str(member.id) not in self.bot.data.profiles[f'{ctx.guild.id}']['nicks_pre']:
				self.bot.data.profiles[f'{ctx.guild.id}']['nicks_pre'][f'{member.id}'] = member.nick
			await ctx.send(f"permanent nick for {member} is now set to `{permanentnick}`", delete_after=3)
			await member.edit(reason="no reason, lol", nick=permanentnick)
		self.bot.data.save_server(ctx.guild.id)
		return

	@commands.Cog.listener("on_member_update")
	async def on_member_update(self, member_before: discord.Member, member_after: discord.Member):
		if not member_before.nick == member_after.nick:
			if not self.bot.data.profiles.get(f'{member_after.guild.id}') is None:
				if not self.bot.data.profiles[f'{member_after.guild.id}'].get("nicks") is None:
					if f'{member_after.id}' in self.bot.data.profiles[f'{member_after.guild.id}']["nicks"]:
						if not self.bot.data.profiles[f'{member_after.guild.id}']["nicks"][
							       f'{member_after.id}'] == member_after.nick:
							print(f'member changed nick to {member_before.nick} while having '
							      f'permanick {self.bot.data.profiles[f"{member_after.guild.id}"]["nicks"][f"{member_after.id}"]}')
							await member_after.edit(
								reason="permanent nickname",
                nick=self.bot.data.profiles[f'{member_after.guild.id}']["nicks"][f'{member_after.id}']
							)


def setup(bot):
	bot.add_cog(UserManagement(bot))
