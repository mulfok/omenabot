import discord.ext.commands

import omenabot


class E(discord.ext.commands.Cog):
	def __init__(self, bot):
		self.bot = bot


def setup(bot: omenabot.OmenaBot):
	bot.add_cog(E(bot))
