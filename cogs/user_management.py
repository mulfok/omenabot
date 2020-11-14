import json
import logging

import discord
from discord.ext import commands

from cogs.general import General
from omenabot import OmenaBot


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
	async def kick(self, ctx: commands.Context, member: discord.Member, *, reason=None):
		perms = ctx.message.author.permissions_in(ctx.channel)
		if perms.administrator or self.bot.config["devs"].get(f"{ctx.author.id}") is not None:
			self.logger.critical(
				f'{member.mention} (ID {member.id}) was kicked from server {ctx.guild.id} with reason: "{reason}".')
			await member.kick(reason=reason)
			await ctx.send(f'{member.mention} was kicked from the server. :hammer:')
		else:
			commands.MissingPermissions(perms.manage_members)

	@commands.command()
	@commands.has_permissions(administrator=True)
	# set params and BAN
	async def ban(self, ctx: commands.Context, member, *, reason=None):
		perms = ctx.message.author.permissions_in(ctx.channel)
		if perms.administrator or not self.bot.config["devs"].get(f"{ctx.author.id}") is None:
			member = ctx.guild.get_member(int(member[3: -1]))
			self.logger.critical(
				f'{member.mention} (ID {member.id}) was banned from server {ctx.guild.id} with reason: "{reason}".')
			await member.ban(reason=reason)
			await ctx.send(f'{member.mention} was banned from the server. :hammer:')
		else:
			commands.MissingPermissions(perms.administrator)

	@commands.command()
	@commands.has_permissions(administrator=True)
	async def unban(this, ctx: commands.Context, *, member):
		# grab server ban list and return
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')

		for ban_entry in banned_users:
			user = ban_entry.user

			if (user.name, user.discriminator) == (member_name, member_discriminator):
				this.logger.critical(f'{member.mention} (ID {member.id}) was unbanned from server {ctx.guild.id}.')
				await ctx.guild.unban(user)
				await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
				return

	@commands.command()
	async def setnick(this, ctx: commands.Context, *value: str):
		if not ctx.author.guild_permissions.manage_nicknames and not ctx.author.guild_permissions.administrator and \
						this.bot.config["devs"].get(f"{ctx.author.id}") is None:
			raise commands.MissingPermissions(discord.permissions.Permissions(permissions=1 << 27))
		if len(ctx.message.mentions) == 1:
			member = ctx.message.mentions[0]
		elif len(value[0]) == len("564489099512381440"):
			member = ctx.guild.get_member(int(value[0]))
		else:
			member = ctx.guild.get_member(int(value[0][2:-1]))
		await ctx.message.delete()
		if this.bot.servers[f'{ctx.guild.id}'].get("nicks") is None:
			this.bot.servers[f'{ctx.guild.id}']["nicks"] = {}
		while isinstance(value, tuple) and isinstance(value[0], tuple):
			value = value[0]
		if len(value) < 2:
			if not this.bot.servers[f'{ctx.guild.id}']["nicks"].get(f'{member.id}') is None:
				this.bot.servers[f'{ctx.guild.id}']["nicks"].pop(f'{member.id}')
				await ctx.send(f"reset permanent nick for {member}", delete_after=3)
				await member.edit(nick=None)
		else:
			permanentnick = ' '.join(value[1:])
			if len(permanentnick) > 32:
				await ctx.send(f"Nickname `{permanentnick}` is too long (32 characters max).", delete_after=7)
				return
			this.bot.servers[f'{ctx.guild.id}']["nicks"][f'{member.id}'] = permanentnick
			await ctx.send(f"permanent nick for {member} is now set to `{permanentnick}`", delete_after=3)
			await member.edit(reason="no reason, lol", nick=permanentnick)
		with open(f'{this.bot.rundir}/private/servers.json', 'w') as f:
			json.dump(this.bot.servers, f, indent=2)
		return


def setup(bot):
	bot.add_cog(UserManagement(bot))
