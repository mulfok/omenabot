import asyncio

import audioop
import discord
import youtube_dl

from discord.ext import commands
from youtube_dl import DownloadError

from omenabot import OmenaBot

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
	'restrictfilenames': True,
	'noplaylist': True,
	'nocheckcertificate': True,
	'ignoreerrors': False,
	'logtostderr': False,
	'quiet': True,
	'no_warnings': True,
	'default_search': 'auto',
	'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
	'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTAudio(discord.AudioSource):

	def __init__(self, original, *, data, volume=0.5):
		if not isinstance(original, discord.AudioSource):
			raise TypeError('expected AudioSource not {0.__class__.__name__}.'.format(original))

		if original.is_opus():
			raise discord.ClientException('AudioSource must not be Opus encoded.')

		self.original = original
		self.volume = volume

		self.data = data

		self.title = data.get('title')
		self.url = data.get('url')
		self.voice_client = None

	@property
	def volume(self):
		"""Retrieves or sets the volume as a floating point percentage (e.g. ``1.0`` for 100%)."""
		return self._volume

	@volume.setter
	def volume(self, value):
		self._volume = max(value, 0.0)

	def cleanup(self):
		self.original.cleanup()

	def read(self):
		ret = self.original.read()
		return audioop.mul(ret, 2, min(self._volume, 2.0))

	@classmethod
	async def from_url(cls, url, *, loop=None, stream=True):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

		if 'entries' in data:
			# take first item from a playlist
			data = data['entries'][0]

		data["req"] = (url, loop, stream)

		filename = data['url'] if stream else ytdl.prepare_filename(data)
		data['filename'] = filename
		ffmpeg_options["before_options"] = "-ss 0"
		return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

	def restart(self, time = 0):
		ffmpeg_options["before_options"] = f"-ss {time}"
		vc = self.voice_client
		self.__init__(discord.FFmpegPCMAudio(self.data['filename'], **ffmpeg_options), data = self.data)
		self.voice_client = vc


class Music(commands.Cog):
	def __init__(this, bot):
		this.bot = bot
		this.current = None
		this.playing = []
		this.loop_mode = "queue"

	@commands.command()
	async def join(this, ctx, *, channel: discord.VoiceChannel):
		"""Joins a voice channel"""

		if ctx.voice_client is not None:
			return await ctx.voice_client.move_to(channel)

		await channel.connect()

	def check_queue(this, error):
		played = this.playing.pop(this.playing.index(this.current)) if this.current in this.playing else None
		if not error and played:
			match played:
				case YTAudio():
					played.restart()
				case _:
					print("matched Wildcard")
					played = None
			if played:
				match this.loop_mode:
					case "queue":
						this.playing.append(played)
					case "single":
						this.playing = [played] + this.playing
					case _:
						print("cool, huh?")
		if this.playing:
			this.current = this.playing[0]
			if played.voice_client:
				this.current.voice_client = played.voice_client
				played.voice_client.play(this.current, after=this.check_queue)

	@commands.command()
	async def loop(this, ctx: commands.Context, loop_mode=None):
		if not loop_mode:
			match this.loop_mode:
				case "queue":
					this.loop_mode = "single"
					await ctx.message.add_reaction("repeat_one")
				case "single":
					this.loop_mode = "none"
					await ctx.message.add_reaction("arrow_right")
				case _:
					this.loop_mode = "queue"
					await ctx.message.add_reaction("repeat")


	@commands.command()
	async def play_local(this, ctx, *, query):
		"""Plays a file from the local filesystem"""

		source = discord.PCMVolumeTransformer(LocalAudio(query))
		this.playing.append(source)
		queued = False
		if not this.current:
			queued = True
			this.current = source
			source.voice_client = ctx.voice_client
			ctx.voice_client.play(source, after=this.check_queue)

		await ctx.send(f'{"Now playing" if not queued else "Queued"}: {query}')

	@commands.command()
	async def play(this, ctx, *, url):
		"""Plays from a url (almost anything youtube_dl supports)"""

		# if hit := [host for host in [] if host in url]:
		# 	await ctx.send(f"links from {' and '.join(hit)} are not supported, sorry")
		# 	raise NotImplementedError

		async with ctx.typing():
			try:
				player = await YTAudio.from_url(url, loop=this.bot.loop)
				this.playing.append(player)
				queued = True
				if not this.current:
					queued = True
					this.current = player
					player.voice_client = ctx.voice_client
					ctx.voice_client.play(player, after=this.check_queue)
			except DownloadError:
				pass

		await ctx.send(f'{"Now playing" if not queued else "Queued"}: {player.title}')

	@commands.command()
	async def cached(this, ctx, *, url):
		"""Streams from a url (same as play, but pre-download)"""

		async with ctx.typing():
			player = await YTAudio.from_url(url, loop=this.bot.loop, stream=False)
			this.playing.append(player)
			queued = False
			if not this.current:
				queued = True
				this.current = player
				player.voice_client = ctx.voice_client
				ctx.voice_client.play(player, after=this.check_queue)

		await ctx.send(f'{"Now playing" if not queued else "Queued"}: {player.title}')

	@commands.command()
	async def volume(this, ctx, volume: str):
		"""Changes the player's volume"""

		if ctx.voice_client is None:
			return await ctx.send("Not connected to a voice channel.")

		if "%" in volume:
			volume = volume.strip("%")
			volume = float(volume) / 100
		else:
			volume = float(volume)

		ctx.voice_client.source.volume = volume
		await ctx.send(f"Changed volume to {volume * 100}%")

	@commands.command()
	async def stop(this, ctx):
		"""Stops and disconnects the bot from voice"""
		this.playing = []
		this.current = None
		ctx.voice_client.stop()
		await ctx.voice_client.disconnect()

	@play_local.before_invoke
	@play.before_invoke
	@cached.before_invoke
	async def ensure_voice(this, ctx):
		if ctx.voice_client is None:
			if ctx.author.voice:
				await ctx.author.voice.channel.connect()
			else:
				await ctx.send("You are not connected to a voice channel.")
				raise commands.CommandError("Author not connected to a voice channel.")


def setup(bot: OmenaBot):
	bot.add_cog(Music(bot))
