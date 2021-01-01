import asyncio
import datetime
import re
import sys
import time
from tkinter.ttk import Checkbutton, Separator

import arrow
import asynctk as atk
from asynctk import messagebox
from asynctk.scrolledtext import AsyncScrolledText
from discord.ext import commands
from discord import Message

from omenabot import OmenaBot


class MockSTDIO:
	"""pretends to be a stdio interface but redirects to a text widget"""

	def __init__(self, io_type, text_widget):
		self.reg = re.compile(r"\[\d+m")
		self.text_widget = text_widget
		self.io_type = io_type
		if io_type == 'stdout':
			self.original_io = sys.stdout
			sys.stdout = self
		elif io_type == 'stderr':
			self.original_io = sys.stderr
			sys.stderr = self
		elif io_type == 'stdin':
			self.original_io = sys.stdin
			sys.stdin = self

	def write(self, text: str):
		self.text_widget['state'] = 'normal'
		self.text_widget.insert(atk.END, self.reg.sub("", string=text))
		self.text_widget['state'] = 'disabled'
		self.original_io.write(text)
		if self.io_type == "stderr":
			pass

	def flush(self, *args, **kw):
		self.original_io.flush(*args, **kw)

	def __del__(self):
		if self.io_type == 'stdout':
			self.original_io = sys.stdout
		elif self.io_type == 'stderr':
			self.original_io = sys.stderr


class GUI(commands.Cog, atk.AsyncTk):

	def qualified_name(this):
		return "gui"

	def __init__(this, bot: OmenaBot):
		atk.AsyncTk.__init__(this, loop=bot.loop)
		this.bot = bot
		this.pending_messages = {}
		this.current_command = None
		this.running_commands = {}

		this.command_frame = atk.AsyncFrame(this)
		this.command_frame.text = AsyncScrolledText(this.command_frame, state='disabled', width=40, height=10)

		this.statistics_frame = atk.AsyncFrame(this)
		this.statistics_frame.clock = atk.AsyncLabel(this.statistics_frame, text="")
		this.statistics_frame.runtime = atk.AsyncLabel(this.statistics_frame, text="")
		this.statistics_frame.guilds = atk.AsyncLabel(this.statistics_frame, text=f'Guilds: {len(bot.guilds)}')
		this.statistics_frame.channels = atk.AsyncLabel(this.statistics_frame,
																										text=f'Channels: {len([i for i in bot.get_all_channels()])}')
		this.statistics_frame.users = atk.AsyncLabel(this.statistics_frame, text=f'Users: {len(bot.users)}')
		this.statistics_frame.emoji = atk.AsyncLabel(this.statistics_frame, text=f'Emoji: {len(bot.emojis)}')

		this.stdout_frame = atk.AsyncFrame(this)
		this.stdout_frame.text = AsyncScrolledText(this.stdout_frame, state='disabled', width=40, height=10)
		this.stdout = MockSTDIO('stdout', this.stdout_frame.text)

		this.stderr_frame = atk.AsyncFrame(this)
		this.stderr_frame.text = AsyncScrolledText(this.stderr_frame, state='disabled', width=40, height=10)
		this.stderr = MockSTDIO('stderr', this.stderr_frame.text)

		this.command_editing_frame = atk.AsyncFrame(this)
		# self.command_editing_frame.menu_button = atk.AsyncMenubutton(self.command_editing_frame, text='Choose a command')
		this.command_editing_frame.command_var = atk.StringVar(this, name="Choose command")
		bot_commands = [(i,) for i in this.bot.commands]
		this.command_editing_frame.option_menu = atk.AsyncOptionMenu(this.command_editing_frame,
																																 this.command_editing_frame.command_var,
																																 bot_commands[0], *bot_commands[0:],
																																 callback=this.make_option)  # , text='Choose a command')

		this.command_cache = bot.commands.copy()

		this.command_editing_frame.hidden_var = atk.IntVar(this)
		this.command_editing_frame.enabled_var = atk.IntVar(this)
		this.command_editing_frame.help = AsyncScrolledText(this.command_editing_frame, width=40, height=10)
		this.command_editing_frame.help_submit = atk.AsyncButton(this.command_editing_frame, text='Submit Helpstring',
																														 callback=this.submit_helpstring)
		this.command_editing_frame.hidden = Checkbutton(this.command_editing_frame, text='Hidden:', command=this.set_hidden,
																										variable=this.command_editing_frame.hidden_var)
		this.command_editing_frame.enabled = Checkbutton(this.command_editing_frame, text='Enabled:',
																										 command=this.set_enabled,
																										 variable=this.command_editing_frame.enabled_var)

		def close(self=this):
			self.bot.loop.create_task(self.bot.close_bot(name="GUI", name_id=-1), name="close task")

		this.close_button = atk.AsyncButton(this, bg="red", callback=close)

		atk.AsyncLabel(this.command_frame, text='Command info:').pack()
		this.command_frame.text.pack()

		atk.AsyncLabel(this.statistics_frame, text='Statistics:').pack()
		this.statistics_frame.clock.pack()
		this.statistics_frame.runtime.pack()
		this.statistics_frame.guilds.pack()
		this.statistics_frame.channels.pack()
		this.statistics_frame.users.pack()

		atk.AsyncLabel(this.stdout_frame, text='STDOut:').pack()
		this.stdout_frame.text.pack()

		atk.AsyncLabel(this.stderr_frame, text='STDErr:').pack()
		this.stderr_frame.text.pack()

		atk.AsyncLabel(this.command_editing_frame, text='Modify commands:').grid(row=0, column=0, columnspan=2)
		Separator(this.command_editing_frame).grid(row=1, column=0, columnspan=2)
		atk.AsyncLabel(this.command_editing_frame, text='Command:', anchor=atk.W).grid(row=2, column=0)
		# self.command_editing_frame.menu_button.grid(row=2, column=1)
		this.command_editing_frame.option_menu.grid(row=2, column=1)
		this.command_editing_frame.help.grid(row=3, column=0, columnspan=2)
		this.command_editing_frame.help_submit.grid(row=4, column=0, columnspan=2)
		this.command_editing_frame.hidden.grid(row=5, column=0)
		this.command_editing_frame.enabled.grid(row=5, column=1)

		this.command_frame.grid(row=0, column=0, rows=2)
		this.stdout_frame.grid(row=2, column=0, rows=2)
		this.stderr_frame.grid(row=4, column=0, rows=2)
		this.statistics_frame.grid(row=0, column=1, rows=2)
		this.command_editing_frame.grid(row=1, column=1, rows=4)
		this.close_button.grid(row=5, column=1, rows=1)

		this.wm_protocol('WM_DELETE_WINDOW', this.cog_unload)
		this.update_clock()
		this.repack()

	def add_pending(this, message: Message):
		now = arrow.now()
		this.pending_messages[message] = now

	async def add_message(this, message: Message, sent_time: arrow.Arrow):
		wid = this.command_frame.text
		wid['state'] = 'normal'
		wid.insert(atk.END, f'[{sent_time.format("HH:mm")}] {message.author.name}: {message.content}\n')
		wid['state'] = 'disabled'

	def repack(this):

		this.command_frame.grid(row=0, column=0, rows=2)
		this.stdout_frame.grid(row=2, column=0, rows=2)
		this.stderr_frame.grid(row=4, column=0, rows=2)
		this.statistics_frame.grid(row=0, column=1, rows=2)
		this.command_editing_frame.grid(row=1, column=1, rows=4)
		this.close_button.grid(row=5, column=1, rows=1)
		this.after(750, this.repack)

	def update_clock(this):
		now = time.strftime("%H:%M:%S", time.gmtime(time.monotonic() + 10800))
		this.statistics_frame.clock.configure(text=now)
		# from omenabot import OmenaBot
		this.statistics_frame.runtime.configure(text=datetime.timedelta(seconds=(
																																										time.monotonic_ns() - this.bot.start_time_ns) // 1000000000))  # OmenaBot.parse_duration((time.monotonic_ns() - self.bot.start_time_ns)//1000000000))

		# call this function again in one second
		this.after(750, this.update_clock)

	async def make_option(this, command):
		command = command[0]
		this.current_command = command
		this.command_editing_frame.help.delete(1.0, atk.END)
		this.command_editing_frame.help.insert(1.0, command.help or '')
		this.command_editing_frame.hidden_var.set(int(command.hidden))
		this.command_editing_frame.enabled_var.set(int(command.enabled))

	@commands.Cog.listener()
	async def on_ready(this):
		this.wm_title(f'{this.bot.user} | Debug GUI')
		this.statistics_frame.guilds['text'] = f'Guilds: {len(this.bot.guilds)}'
		this.statistics_frame.channels['text'] = f'Channels: {len([i for i in this.bot.get_all_channels()])}'
		this.statistics_frame.users['text'] = f'Users: {len(this.bot.users)}'
		this.statistics_frame.emoji['text'] = f'Emoji: {len(this.bot.emojis)}'

	def cog_unload(self):
		del self.stdout
		del self.stderr
		asyncio.ensure_future(self.destroy())

	async def check(this, message):
		if this.current_command is None:
			await messagebox.showerror(f'No command selected for which to {message}!')
			return False
		return True

	async def submit_helpstring(self):
		if self.check("submit the helpstring"):
			self.current_command.help = self.command_editing_frame.help.get('1.0', 'end-1c')

	def set_hidden(self):
		if self.check("hide/show"):
			self.current_command.hidden = self.command_editing_frame.hidden_var.get()

	def set_enabled(self):
		if self.check("enable/disable"):
			self.current_command.enabled = self.command_editing_frame.enabled_var.get()

	@commands.Cog.listener()
	async def on_command_completion(self, ctx):
		running = [i for i in self.running_commands.items() if i[0][2] == ctx.command.qualified_name]
		ctx.command
		finished_time = arrow.now() - self.running_commands.pop((ctx.author.id, ctx.channel.id, ctx.command.qualified_name))
		wid = self.command_frame.text
		wid['state'] = 'normal'
		wid.insert(atk.END,
							 f'[Finished in {round(finished_time.total_seconds() * 1000, 1)}ms] {ctx.author.name}: {ctx.prefix}{ctx.command.qualified_name}\n')
		wid['state'] = 'disabled'

	@commands.Cog.listener()
	async def on_command(self, ctx):
		init = arrow.now()
		running = [i for i in self.running_commands.items() if i[0][2] == ctx.command.qualified_name]
		print(len(running), running)
		self.running_commands[ctx.author.id, ctx.channel.id, ctx.command.qualified_name, len(running)] = init
		wid = self.command_frame.text
		wid['state'] = 'normal'
		wid.insert(atk.END, f'[{init.format("HH:mm")}] {ctx.author.name}: {ctx.prefix}{ctx.command.qualified_name}\n')
		wid['state'] = 'disabled'

	@commands.Cog.listener()
	async def on_guild_join(self, guild):
		self.statistics_frame.guilds['text'] = f'Guilds: {len(self.bot.guilds)}'

	@commands.Cog.listener()
	async def on_guild_remove(self, guild):
		self.statistics_frame.guilds['text'] = f'Guilds: {len(self.bot.guilds)}'

	@commands.Cog.listener()
	async def on_guild_channel_create(self, channel):
		self.statistics_frame.channels['text'] = f'Channels: {len([i for i in self.bot.get_all_channels()])}'

	@commands.Cog.listener()
	async def on_guild_channel_delete(self, channel):
		self.statistics_frame.channels['text'] = f'Channels: {len([i for i in self.bot.get_all_channels()])}'

	@commands.Cog.listener()
	async def on_member_join(self, member):
		self.statistics_frame.users['text'] = f'Users: {len(self.bot.users)}'

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		self.statistics_frame.users['text'] = f'Users: {len(self.bot.users)}'

	@commands.Cog.listener()
	async def on_guild_emojis_update(self, guild, before, after):
		self.statistics_frame.emoji['text'] = f'Emoji: {len(self.bot.emojis)}'

	async def runme(this):
		while True:
			try:
				await this.tick()
				try:
					if len(this.pending_messages) > 0:
						for message in this.pending_messages:
							time = this.pending_messages.pop(message)
							await this.add_message(message, time)
					if this.command_cache != this.bot.commands:
						bot_commands = this.bot.commands
						bot_commands = [(i,) for i in bot_commands]
						this.command_editing_frame.option_menu = atk.AsyncOptionMenu(this.command_editing_frame,
																																				 this.command_editing_frame.command_var,
																																				 bot_commands[0], *bot_commands[0:],
																																				 callback=this.make_option)  # , text='Choose a command')
						this.command_cache = this.bot.commands.copy()
				except:
					import traceback
					traceback.print_exc()
			except:
				return
			await asyncio.sleep(0.01)


def setup(bot):
	cog = GUI(bot)
	bot.add_cog(cog)
	bot.loop.create_task(cog.runme())
