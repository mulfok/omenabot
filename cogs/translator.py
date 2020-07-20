import discord
import logging
from discord.ext import commands

def setup(bot: discord.ext.commands.bot.Bot):
	bot.add_cog(Translator(bot))

class Translator(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(name='translate', invoke_without_subcommand=True)
	async def tran(self, ctx: commands.Context):
		await ctx.send("**WARNING**: lenrik is in process of implementing this feature!")
		await ctx.send("**lenrik**: right now it does nothing :stuck_out_tongue:")

	def cog_unload(self):
		logging.info("Translator terminated.")
