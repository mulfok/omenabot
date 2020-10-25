import logging

import discord
from discord.ext import commands
from main import OmenaBot


class User_managment(commands.Cog):
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
	async def unban(self, ctx: commands.Context, *, member):
		# grab server ban list and return
		banned_users = await ctx.guild.bans()
		member_name, member_discriminator = member.split('#')

		for ban_entry in banned_users:
			user = ban_entry.user

			if (user.name, user.discriminator) == (member_name, member_discriminator):
				self.logger.critical(f'{member.mention} (ID {member.id}) was unbanned from server {ctx.guild.id}.')
				await ctx.guild.unban(user)
				await ctx.send(f'Unbanned {user.mention}. Welcome back! :wave:')
				return


def setup(bot):
	bot.add_cog(User_managment(bot))
