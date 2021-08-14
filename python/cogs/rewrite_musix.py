import asyncio
import inspect
import logging
import sys
import threading
import time
import traceback
import typing
from asyncio import coroutine

import discord
from discord import ClientException, AudioSource, opus

from omenabot import OmenaBot
from discord.ext import commands, tasks

log = logging.getLogger(__name__)


class Player(threading.Thread):
	DELAY = discord.player.OpusEncoder.FRAME_LENGTH / 1000.0

	def __init__(self, source, client, *, state=None):
		threading.Thread.__init__(self)
		self.daemon = True
		self.source = source
		self.client = client
		self.state = state

		self._end = threading.Event()
		self._resumed = threading.Event()
		self._resumed.set()  # we are not paused
		self._current_error = None
		self._connected = client._connected
		self._lock = threading.Lock()

	def _do_run(self):
		self.loops = 0
		self._start = time.perf_counter()

		# getattr lookup speed ups
		play_audio = self.client.send_audio_packet
		self._speak(True)

		while not self._end.is_set():
			# are we paused?
			if not self._resumed.is_set():
				# wait until we aren't
				self._resumed.wait()
				continue

			# are we disconnected from voice?
			if not self._connected.is_set():
				# wait until we are connected
				self._connected.wait()
				# reset our internal data
				self.loops = 0
				self._start = time.perf_counter()

			self.loops += 1
			data = self.source.read()

			if not data:
				if not self.state.queue:
					self.stop()
					break

			play_audio(data, encode=not self.source.is_opus())
			next_time = self._start + self.DELAY * self.loops
			delay = max(0, self.DELAY + (next_time - time.perf_counter()))
			time.sleep(delay)

	def run(self):
		try:
			self._do_run()
		except Exception as exc:
			self._current_error = exc
			self.stop()
		finally:
			self.source.cleanup()
			self._call_after()

	def _call_after(self):
		error = self._current_error

		# if self.after is not None:
		# 	try:
		# 		if inspect.iscoroutinefunction(self.after):
		# 			fut = asyncio.run_coroutine_threadsafe(self.after(error), self.client.loop)
		# 			fut.result()
		# 		else:
		# 			self.after(error)
		# 	except Exception as exc:
		# 		log.exception('Calling the after function failed.')
		# 		exc.__context__ = error
		# 		traceback.print_exception(type(exc), exc, exc.__traceback__)
		# elif error:
		# 	msg = 'Exception in voice thread {}'.format(self.name)
		# 	log.exception(msg, exc_info=error)
		# 	print(msg, file=sys.stderr)
		# 	traceback.print_exception(type(error), error, error.__traceback__)

	def stop(self):
		self._end.set()
		self._resumed.clear()
		self._speak(False)

	def pause(self, *, update_speaking=True):
		self._resumed.clear()
		if update_speaking:
			self._speak(False)

	def resume(self, *, update_speaking=True):
		self.loops = 0
		self._start = time.perf_counter()
		self._resumed.set()
		if update_speaking:
			self._speak(True)

	def is_playing(self):
		return self._resumed.is_set() and not self._end.is_set()

	def is_paused(self):
		return not self._end.is_set() and not self._resumed.is_set()

	def _set_source(self, source):
		with self._lock:
			self.pause(update_speaking=False)
			self.source = source
			self.resume(update_speaking=False)

	def _speak(self, speaking):
		try:
			asyncio.run_coroutine_threadsafe(self.client.ws.speak(speaking), self.client.loop)
		except Exception as e:
			log.info("Speaking call in player failed: %s", e)


class Music(commands.Cog):
	servers = {}

	def __init__(self, bot: OmenaBot):
		self.bot = bot

	@commands.command("connect", aliases=["join"])
	async def join(self, context: commands.Context):
		if f"{context.guild.id}" not in self.servers:
			vc: discord.VoiceClient = await context.author.voice.channel.connect(reconnect=True, timeout=3)
			await vc.ws.speak(False)
			@typing.NamedTuple
			class State:
				voice_client = vc
				loop_mode = "queue"
				pos = -1
				queue = {}
			self.servers[f"{context.guild.id}"] = State  # {"voice_client": vc, "loop_mode": "queue", "pos": -1, "queue": {}}
			await context.message.add_reaction("🎵")
		else:
			await context.message.add_reaction("❌")
			await context.send("Already connected to the voice chat in this guild.")

	@commands.command("disconnect", aliases=["leave"])
	async def leave(self, context: commands.Context):
		if f"{context.guild.id}" in self.servers:
			await self.servers[f"{context.guild.id}"].voice_client.disconnect()
			del self.servers[f"{context.guild.id}"]
			await context.message.add_reaction("👋")
		else:
			await context.message.add_reaction("❌")
			await context.send("Not connected to any voice chat in this guild.")

	async def check_joined(self, context: commands.Context):
		if f"{context.guild.id}" not in self.servers:
			await self.join(context)

	def _play(self, voice_client, source, *, state=None):

		if not voice_client.is_connected():
			raise ClientException('Not connected to voice.')

		if voice_client.is_playing():
			raise ClientException('Already playing audio.')

		if not isinstance(source, AudioSource):
			raise TypeError('source must be an AudioSource not {0.__class__.__name__}'.format(source))

		if not voice_client.encoder and not source.is_opus():
			voice_client.encoder = opus.Encoder()

		voice_client._player = Player(source, voice_client, state=state)
		voice_client._player.start()

	@commands.command("play")
	@commands.before_invoke(check_joined)
	async def play(self, context: commands.Context, *query: str):
		print(" ".join(query))
		insert_pos = len(self.servers[f"{context.guild.id}"].queue)
		self.servers[f"{context.guild.id}"].queue[insert_pos] = {"query": " ".join(query)}
		vc: discord.VoiceClient = self.servers[f"{context.guild.id}"].voice_client
		self._play(vc, "", state=self.servers[f"{context.guild.id}"])
		print(self.servers)
		pass


def setup(bot):
	bot.add_cog(Music(bot))
