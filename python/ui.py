import asyncio
from asyncio import threads
import time
import tkinter as tk
from io import TextIOWrapper, FileIO

from omenabot import OmenaBot


class SampleApp(tk.Tk):
	def __init__(self, *args, **kwargs):
		tk.Tk.__init__(self, *args, **kwargs)
		loop = asyncio.new_event_loop()
		self.bot = OmenaBot(loop=loop)
		self.clock = tk.Label(self, text="")
		self.clock.grid(row=1, column=1)
		self.textFiled = tk.Text(self, state=tk.DISABLED)
		self.textFiled.grid(row=0, column=0, rows=3)
		self.stopButton = tk.Button(self, text="Stop Bot", padx=10, pady=10, command=self.stop_bot)
		self.stopButton.grid(row=0, column=1)
		self.output = TextIOWrapper(FileIO('/home/tent/stdpipe', mode='wb'))

		# start the clock "ticking"

		self.update_clock()
		self.bot_loop = loop

	def stop_bot(self):
		print("stop pressed")

		self.bot_loop.create_task(self.bot.close_bot(), name="stop").done()

	def update_clock(self):
		now = time.strftime("%H:%M:%S", time.gmtime())
		self.clock.configure(text=now)

		# call this function again in one second
		self.after(1000, self.update_clock)

	async def run(self, n=0):
		await threads.to_thread(self.tk.mainloop(n))
		# await self.bot.run_bot(output=self.output, loop=asyncio.new_event_loop()) no longer exists


if __name__ == "__main__":
	app = SampleApp()
	asyncio.run(app.run())
