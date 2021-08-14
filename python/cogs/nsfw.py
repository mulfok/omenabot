import argparse
import asyncio
import io
import json
import random
import re
from pathlib import Path

import discord
import pixivapi
import requests
from discord.ext import commands
from omenabot import OmenaBot
from pixivapi import Client, Size, LoginError, Illustration


def setup(bot: OmenaBot):
	bot.add_cog(NSFW(bot))


class FakeFile(io.IOBase):
	def __init__(self, data=b''):
		self.w_cursor = 0
		self.cursor = 0
		self.data = data

	def tell(self) -> int:
		return self.cursor

	def seekable(self) -> bool:
		return True

	def readable(self) -> bool:
		return True

	def write(self, data):
		self.w_cursor += len(data)
		self.data += data

	def seek(self, pos: int, **kwargs):
		self.cursor = pos

	def read(self, length: int):
		# if self.cursor + length > len(self.data):
		# 	raise
		red_data = self.data[self.cursor:self.cursor + length]
		self.cursor += length
		return red_data

	def __str__(self):
		return self.data

	def open(self):
		return self

	def __enter__(self):
		return self


class FakeDir:
	file: FakeFile

	def __init__(self):
		self.file = FakeFile()

	def __truediv__(self, other):
		self.filename = other
		return self

	def mkdir(self, *args, **kwargs):
		pass

	def open(self, mode: str, *args, **kwargs):
		return self

	def __enter__(self):
		return self.file

	def __exit__(self, exc_type, exc_val, exc_tb):
		pass


class NSFW(commands.Cog):
	def __init__(self, bot: OmenaBot):
		self.bot = bot
		self.client = Client(language='English')
		# self.auth_pixiv()
		self.pixiv_parser = argparse.ArgumentParser(exit_on_error=False)
		self.pixiv_parser.add_argument("query", nargs="*", default=["Genshin", "impact"])
		self.pixiv_parser.add_argument("-tags", nargs="*", default=[])
		self.pixiv_parser.add_argument("-hide", nargs="*", default=["R-18", 'R-17.9', 'R-18G'])

	def auth_pixiv(self):
		token_data = {}
		try:
			with open(self.bot.rundir / "private" / "pixiv.json", "r") as f:
				token_data = json.load(f)
				refresh_token = token_data["refresh"]
			self.client.authenticate(refresh_token)
		except (FileNotFoundError, LoginError):
			print("FNFE")
			try:
				print("no refresh token found")
				self.client.login(
					"m.maxim.max44@gmail.com",
					"max!m0314"
				)
				token_data["refresh"] = self.client.refresh_token
				with open(self.bot.rundir / "private" / "pixiv.json", "w") as f:
					json.dump(token_data, f)
			except LoginError:
				try:
					print("no refresh token found")
					self.client.login(
						"lenrik1589",
						"max!m0314"
					)
					token_data["refresh"] = self.client.refresh_token
					with open(self.bot.rundir / "private" / "pixiv.json", "w") as f:
						json.dump(token_data, f)
				except LoginError:
					try:
						self.client.login(
							"user_xerj4578",
							"max!m0314"
						)
						token_data["refresh"] = self.client.refresh_token
						with open(self.bot.rundir / "private" / "pixiv.json", 'w') as f:
							json.dump(token_data, f)
					except LoginError:
						print("failed to login using mail, nickname and pixiv id")

	async def d_pixiv(self, illustraton: Illustration, size: Size) -> (bytes, str):
		from pixivapi.models import splitext
		referer = (
			"https://www.pixiv.net/member_illust.php?mode=medium"
			f"&illust_id={illustraton.id}"
		)

		url = illustraton.image_urls[size]
		if not url:
			if illustraton.meta_pages:
				url = illustraton.meta_pages[0][size]
			else:
				return b'', ''
		print(url)
		ext = splitext(url)[1]
		response = illustraton.client.session.get(
			url=url,
			headers={"Referer": referer},
			stream=True
		)
		f = b''
		for chunk in response.iter_content(chunk_size=1024):
			if chunk:
				f += chunk
				await asyncio.sleep(0.00001)
		return f, ext

	@commands.is_nsfw()
	@commands.command("pixiv", hidden=True)
	async def pixiv(self, context: commands.Context, *args: str):
		if isinstance(context.channel, discord.DMChannel) or context.channel.is_nsfw:
			message = await context.send("searching")
			parsed = self.pixiv_parser.parse_args(args)
			query = " ".join(parsed.query)
			done = False
			while not done:
				try:
					try:
						print(f"checking for id {query}")
						illust = await self.bot.loop.run_in_executor(None, self.client.fetch_illustration, int(query))
						done = True
					except (requests.RequestException, ValueError, TypeError):
						print("searching")
						num = random.randint(0, 150)
						response = await self.bot.loop.run_in_executor(
							None,
							self.client.search_illustrations,
							query,
							pixivapi.SearchTarget.TITLE_AND_CAPTION,
							pixivapi.Sort.DATE_DESC,
							None,
							num
						)
						try:
							illust = response["illustrations"][0]
							done = True
						except IndexError:
							print("no illustrations found")
							await message.edit(content=f'nothing found for "{query}"')
							return
				except (pixivapi.BadApiResponse, pixivapi.AuthenticationRequired) as error:
					if isinstance(error, pixivapi.AuthenticationRequired):
						print("not authenticated")
						self.auth_pixiv()
					else:
						error_json = json.load(io.StringIO(error.args[1]))
						if error.args[0] == "Status code: 404":
							await message.edit(content=error_json["error"]["user_message"])
						elif error.args[0] == "Status code: 400":
							if error_json["error"]["message"].startswith(
											"Error occurred at the OAuth process. Please check your Access Token"):
								print("not authenticated")
								self.auth_pixiv()
								continue
							await message.edit(content=f'request failed {error_json["error"]["message"]}')
						else:
							await message.edit(content=f"request to pixiv api failed with error {error}")
						print("request failed", error)
						return
			await message.edit(
				content="<https://www.pixiv.net/member_illust.php?mode=medium"
				        f"&illust_id={illust.id}>\ndownloading image…"
			)
			print("starting download")
			image_data, ext = await self.d_pixiv(illust, size=Size.ORIGINAL)
			if len(image_data) > 8_000_000 or not image_data:
				print("original too big")
				image_data, ext = await self.d_pixiv(illust, size=Size.LARGE)
				if len(image_data) > 8_000_000 or not image_data:
					print("large too big")
					image_data, ext = await self.d_pixiv(illust, size=Size.SQUARE_MEDIUM)
					if len(image_data) > 8_000_000 or not image_data:
						print("square medium too big")
						image_data, ext = await self.d_pixiv(illust, size=Size.MEDIUM)
			print("downloaded")
			await message.delete()
			message = await context.send(
				content="<https://www.pixiv.net/member_illust.php?mode=medium"
				        f"&illust_id={illust.id}>",
				files=[discord.File(FakeFile(image_data), filename=f"{illust.id}{ext}")]
			)
			await message.edit(embed=None)
		else:
			await context.send("this is not an nsfw channel")

	def cog_unload(self):
		self.client.session.close()
