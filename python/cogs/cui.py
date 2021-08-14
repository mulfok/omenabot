import colorsys
import functools
import re
import sys
import traceback
from datetime import datetime
from typing import Optional

import discord
from blessed import Terminal
from discord.ext.commands import Cog
from discord.ext.tasks import loop

from omenabot import OmenaBot

control_seq_re = re.compile(r"(\[[\d;]+m|\?--cur--\?)")


def wrap(line: str, length) -> [str]:
	# try:
	# print("wrap")
	splits = control_seq_re.split(line)
	# print(splits)
	splits = [splits[i] for i in range(len(splits) + 1) if (i + 1) % 2]
	codes = control_seq_re.findall(line)
	# print(splits, codes)
	indecies = []
	acc = ""
	for split in splits:
		indecies.append(len(acc))
		acc += split
	indecies.pop(0)
	if len(codes) < len(indecies):
		indecies.pop(0)
	codes.reverse()
	indecies.reverse()
	line = "".join(splits)
	wrapped = [line[i: min(len(line), i + length)] for i in range(0, len(line), length)]
	wrapped = wrapped or ['']
	for index in range(len(indecies)):
		key, val = codes[index], indecies[index]
		y, x = divmod(val, length)
		wrapped[y] = f"{wrapped[y][:x]}{key}{wrapped[y][x:]}"
	# except Exception as e:
	# 	print(f"[{datetime.now().timestamp()}] {e}")

	return wrapped


class Cui(Cog):
	op_names = {i: str(i) for i in range(15)}
	op_names.update({
		-3: "Not discord.gateway.DiscordWebSocket",
		-1: "Connecting",
		7: "Reconnecting",
		11: "Heartbeat"
	})

	@property
	def qualified_name(self):
		return "cui"

	def __init__(self, bot: OmenaBot):
		self.cur = 0
		self.console_text = "?--cur--?"
		self.frame = 0
		self.bot = bot
		self.key = ""
		self.input_buffer = ""
		self.term = Terminal()
		# self.background = self.term.on_color_rgb(*[int(f * 255) for f in colorsys.hsv_to_rgb(0.9, 0.7, 0.9)])
		# self.darkground = self.term.on_color_rgb(0xb0, 0x0b, 0x69)
		self.term.number_of_colors = 1 << 24
		# self.background = self.term.on_color_rgb(*[int(f * 255) for f in colorsys.hsv_to_rgb(0.3, 0.7, 0.9)])
		self.foreground = self.term.color_rgb(*[int(f * 255) for f in colorsys.hsv_to_rgb(0.6, 0.4, 0.5)])
		self.background = self.term.on_color_rgb(*[int(f * 255) for f in colorsys.hsv_to_rgb(333 / 360, 0.90, 0.97)])
		self.fullground = self.foreground + self.background
		self.darkground = self.term.on_color_rgb(*[int(f * 255) for f in colorsys.hsv_to_rgb(337 / 360, 0.84, 0.81)])
		# self.darkground = self.term.on_color_rgb(0x0b, 0xb0, 0x69)
		self.raw_mode = self.term.raw()
		self.raw_mode.__enter__()
		self.bot.output.double(False)
		self.print = functools.partial(print, file=self.bot.output.other, end="", flush=True)
		self.clear()
		self.redraw(self.console_text)
		try:
			self.cli_task.start()
			self.update_gui.start()
			self.update_time.start()
		except BaseException as e:
			print(e.__traceback__)
			print(e)

	y = 0

	def clear(self):
		line = self.background(" " * self.term.width)
		for self.y in range(self.term.height):
			with self.term.location(0, self.y):
				self.print(line)
			self.y += 1
		else:
			self.y = 0

	def redraw(self, buffer: str = ""):
		footer = str(datetime.now())
		n, m = 0, 0
		with self.term.hidden_cursor():

			line = f"{self.fullground}" \
			       f"{len(self.bot.all_commands)} commands, " \
			       f"{len(self.bot.guilds)} guilds, " \
			       f"{'Ready' if self.bot.is_ready() else 'Connecting or Reconnecting'}"
			# f"{self.op_names[self.bot.ws.latest_op if isinstance(self.bot.ws, DiscordWebSocket) else -3]}"

			with self.term.location(1, 1):
				self.print(line)

			offset = 0
			for num, line in enumerate(buffer.split("\n")):
				sublines = wrap(line, self.term.width - 5)
				for subline in sublines:
					try:
						n = subline.index("?--cur--?") + offset
						m = num
					except ValueError:
						pass
					with self.term.location(1, 3 + num + offset):
						self.print(
							f"{self.fullground}" +
							(f"{num}: {''.join(subline.split('?--cur--?'))}".ljust(self.term.width - 5, " "))
						)
					offset += 1
				offset -= 1

			line = sys.stdout.getvalue()
			lines = line.split("\n")
			if len(lines) > 10000:
				sys.stdout.setvalue("\n".join(lines[-10000:]))
			lines = lines[max(
				0,
				len(lines) - self.term.height + 5 + len(self.bot.extensions) + len(buffer.split("\n")) + offset
			):]
			wrapped = []
			for line in lines:
				wrapped += wrap(line, self.term.width - 2)
			lines = wrapped[max(
				0,
				len(wrapped) - self.term.height + 5 + len(self.bot.extensions) + len(buffer.split("\n")) + offset
			):]
			for num, line in enumerate(lines):
				with self.term.location(1, 3 + num + 1 + len(buffer.split("\n"))):
					self.print(self.darkground(line.ljust(self.term.width - 2, " ")))

			for y in range(3 + len(buffer.split("\n")) + len(lines) + offset, self.term.height - 2 - len(self.bot.extensions)):
				with self.term.location(1, y):
					self.print(self.darkground(" " * (self.term.width - 2)))

			with self.term.location(self.term.width - 24, self.term.height - 1 - 1):
				self.print(self.fullground + footer[:22])
			gets = {k: v for k, v in self.bot.extensions.items()}
			# gets.update({k: v for k, v in self.bot.cogs.items()})
			for num, cog in enumerate(gets):
				with self.term.location(1, self.term.height - 1 - len(gets) + num):
					val = gets[cog]
					if isinstance(val, Cog):
						self.print(f"{self.fullground}{num}, Cog: {val.qualified_name}")
					elif isinstance(val, type(sys)):
						self.print(f"{self.fullground}{num}: {val.__package__}/{val.__name__.lstrip(val.__package__)[1:]}")
					else:
						self.print(f"{self.fullground}{num}: {val}")
		self.print(self.term.move_xy(4 + n, 3 + m))
		# range_y = range(0, term.height - 1)
		# range_x = range(0, term.width)
		# for y in range_y:
		# 	for x in (this_x := iter(range_x)):
		# 		with term.location(x, y):
		# 			ratio = ((y + x + frame) % (term.height + term.width * 4)) / (term.height - 1 + term.width) / 4
		# 			h0, s0, v0 = colorsys.rgb_to_hsv(0xb0 / 255, 0x0b / 255, 0x69 / 255)
		# 			h, s, v = colorsys.rgb_to_hsv(0x04 / 255, 0x20 / 255, 0x69 / 255)
		# 			h0, h = 0, 1
		# 			s0, s = 1, 1
		# 			v0, v = .75, .75
		# 			r, g, b = (h0 + (h - h0) * ratio, s0 + (s - s0) * ratio, v0 + (v - v0) * ratio)
		# 			r, g, b = colorsys.hsv_to_rgb(r, g, b)
		# 			if y == term.height - 3 and term.width - 1 - len(footer) <= x < term.width - 1:
		# 				# print(footer, term.width - 1, x, footer[pos])
		# 				print(
		# 					f"{term.on_color_rgb(int(r * 255), int(g * 255), int(b * 255))}{footer[x - term.width + 1 + len(footer)]}")
		# 			else:
		# 				print(f"{term.on_color_rgb(int(r * 255), int(g * 255), int(b * 255))}{' ' * min(4, term.width - x)}")
		# 				try:
		# 					if y == term.height - 3:
		# 						for i in range(0, min(3, -(x - term.width + 1 + 1 + len(footer)), term.width - 3 - x)):
		# 							next(this_x)
		# 					else:
		# 						next(this_x)
		# 						next(this_x)
		# 						next(this_x)
		# 				except StopIteration:
		# 					pass
		self.frame += 1

	class DummyMessage(discord.Message):
		def __init__(self, *args, **kwargs):
			kwargs["data"].update({
				"id": "-1",
				"attachments": [],
				"embeds": [],
				"edited_timestamp": datetime.now().isoformat(),
				"type": discord.MessageType.default.value,
				"pinned": False,
				"mention_everyone": False,
				"tts": False,
			})
			super(Cui.DummyMessage, self).__init__(*args, **kwargs)

		async def delete(self, *, delay: Optional[float] = None) -> None:
			pass

	@loop(seconds=0.001)
	async def cli_task(self):
		try:
			from blessed.keyboard import Keystroke
			match self.key:
				case str('', name=None, code=None):
					pass
				case str(name="KEY_LEFT") if self.cur < len(self.input_buffer):
					self.cur += 1
				case str(name="KEY_RIGHT") if self.cur > 0:
					self.cur -= 1
				case str(name="KEY_BACKSPACE") if len(self.input_buffer) - self.cur:
					buffer = self.input_buffer
					self.input_buffer = f'{buffer[:len(buffer) - self.cur - 1]}{buffer[len(buffer) - self.cur:]}'
				case str(name='KEY_ESCAPE'):
					self.clear()
					self.redraw()
				case str(name="KEY_INSERT"):
					try:
						dev = await self.bot.fetch_user(746090211087351900)
						message = self.DummyMessage(state=self.bot.user._state, channel=await dev.create_dm(), data={
							"content": self.input_buffer,
						})
						message.author = dev
						await self.bot.on_message(message)
						self.input_buffer = ""
					except Exception as e:
						traceback.print_exception(e, file=self.bot.output)
				case '\x03':
					await self.bot.close()
					return
				case str(val, name=name, code=code, is_sequence=seq):
					if not val.isprintable():
						print((str(val), name, code, seq))
					if name == "KEY_ENTER":
						char = "\n"
					elif val == '\t':
						char = val
					elif not val.isprintable():
						char = ""
					else:
						char = val
					buffer = self.input_buffer
					self.input_buffer = f'{buffer[:len(buffer) - self.cur]}{char}{buffer[len(buffer) - self.cur:]}'
			if self.key:
				buffer = self.input_buffer
				self.console_text = f'''{buffer[:len(buffer) - self.cur]}?--cur--?{buffer[len(buffer) - self.cur:]}'''
				self.redraw(self.console_text)
			self.key = await self.bot.loop.run_in_executor(None, self.term.inkey, 0.)
		except BaseException as e:
			traceback.print_exception(e, file=self.bot.output)

	@loop(seconds=0.1)
	async def update_gui(self):
		pass

	# self.clear()
	# self.redraw(self.console_text)

	@loop(seconds=0.05)
	async def update_time(self):
		footer = str(datetime.now())
		with self.term.hidden_cursor(), self.term.location(self.term.width - 24, self.term.height - 2):
			self.print(self.fullground + footer[:22])

	def cog_unload(self):
		try:
			self.clear()
			self.raw_mode.__exit__(None, None, None)
			self.bot.output.double(True)
			self.cli_task.stop()
			self.update_gui.stop()
			self.update_time.stop()
		finally:
			pass


def setup(bot: OmenaBot):
	bot.add_cog(Cui(bot))
