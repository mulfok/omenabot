import logging
import re

import discord
from deep_translator import GoogleTranslator, DeepL
# import httpx as httpx
from discord.ext import commands

import omenabot


def setup(bot: omenabot.OmenaBot):
	bot.add_cog(Translator(bot))


class Translator(commands.Cog):
	def __init__(self, bot: omenabot.OmenaBot):
		self.bot = bot
		# self.client = httpx.Client()
		self.gtrans = GoogleTranslator(source='auto', target='en')
		self.deepl = DeepL(api_key=self.bot.data.tokens["deepl token"], source="en", target="en", use_free_api=True)
		self.exp = re.compile("(?: ?,? ?(source|target|engine) ?= ?(\w+))")

	# del self.bot.tokens["deepl token"]

	@commands.Cog.listener("on_raw_reaction_add")
	async def raw_check_xp(self, payload: discord.RawReactionActionEvent):
		guild: discord.Guild = self.bot.get_guild(payload.guild_id)
		if guild:
			channel: discord.TextChannel = guild.get_channel(payload.channel_id)
			if channel and isinstance(channel, discord.TextChannel):
				message = await channel.fetch_message(payload.message_id)
				if not payload.emoji.id and payload.event_type == "REACTION_ADD" and payload.emoji.name == '👂':
					await message.remove_reaction(payload.emoji, payload.member)
					# self.request_deepl_translation(message.content)
					embed = discord.Embed()
					embed.set_author(
						name=message.author.display_name,
						url=f"https://discord.com/channels/@me/{message.author.id}",
						icon_url=message.author.avatar.url
					)
					embed.add_field(name="Spanish", value=message.content)
					embed.add_field(name="English ", value=self.gtrans.translate(message.content))
					embed.add_field(name="message", value=f"[jump]({message.jump_url})")
					await payload.member.send("", embed=embed)

	@commands.command(name='translate', invoke_without_subcommand=True)
	async def tran(self, context: commands.Context, *text: str, engine="google", source="es", target="en"):
		message: str = context.message.content
		comm: commands.Command = context.command
		clean_cont = message.lstrip(context.prefix).lstrip(comm.name)
		opts = {match.group(1): match.group(2) for match in self.exp.finditer(clean_cont)}
		opts["engine"] = "google" if "engine" not in opts else opts["engine"]
		opts["source"] = "es" if "source" not in opts else opts["source"]
		opts["target"] = "en" if "target" not in opts else opts["target"]
		clean_cont = self.exp.sub("", clean_cont)
		embed = discord.Embed() \
			.add_field(name="Source language", value=opts["source"]) \
			.add_field(name="Target language", value=opts["target"]) \
			.add_field(name="Translation engine", value=opts["engine"])

		# await context.send(opts)
		# await context.send(clean_cont)
		if opts["engine"] in ["google"]:
			value = self.gtrans.translate(clean_cont, sl=opts["source"], tl=opts["target"])
			await context.send(embed=embed)
		elif opts["engine"] in ["deepl"]:
			value = self.deepl.translate(clean_cont, source_lang=opts["source"], target_lang=opts["target"])
		else:
			value = 'incorrect engine key, correct are: "`google`", "`deepl`"'
		embed.add_field(name="Translation", value=value)
		await context.send(embed=embed)

	def cog_unload(self):
		logging.info("Translator terminated.")
