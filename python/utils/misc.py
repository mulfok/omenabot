import argparse

import discord
from discord.ext import commands
from discord.ext.commands import Context


# timeparser = argparse.ArgumentParser()
# timeparser.add_argument("1")


def get_time(*time: str):
	import re
	from datetime import datetime, timedelta
	time = " ".join(time)
	# try:
	# 	modifier = re.compile("-?\\d+").sub("", time)
	# 	time_i = int(time[:-len(modifier)])
	# 	if modifier == 'a':
	# 		return datetime.fromtimestamp(time_i)
	# 	else:
	# 		timedelta()
	# 		modifier = {
	# 			"s": timedelta(seconds=1),
	# 			"m": 60,
	# 			"h": 3600,
	# 			"d": 86400,
	# 			"M": 2592000,
	# 			"y": 31557600
	# 		}[modifier]
	#
	# 		time_i *= modifier
	# 		return datetime.now() + time_i
	# except (ValueError, KeyError):
	import dateparser
	return dateparser.parse(time, languages=['en', 'es'])


def roll_one(dice: int):
	import random
	return random.randrange(dice) + 1


def roll(dices: int, dice: int, keep: int):
	rolls = [roll_one(dice) for _ in range(dices)]
	rolls.sort()
	rolls = rolls[len(rolls) - keep:]
	return rolls


def get_stat():
	rolled = roll(4, 6, 3)
	stat = 0
	for i in range(3):
		stat += rolled[i]
	return f"{stat}({int((stat + 1) / 2) - 5})"


def find_member(message: discord.Message, alternative: str):
	member = None
	if message.mentions:
		member = message.mentions[0]
		print(f"using mention {member}")
	else:  # len(alternative) == len("564489099512381440"):
		try:
			member = message.guild.get_member(int(alternative))
		except ValueError:
			pass
		print(f"using id strat: {member}")
	if not member:
		try:
			member = message.guild.get_member(int(alternative[2:-1]))
		except ValueError:
			pass
		print(f"using alt id strat: {member}")
	if not member:
		member = discord.utils.find(lambda m: m.name.lower().startswith(alternative.lower()), message.guild.members)
		print(f"using discord.py's find() with start strat: {member}")
	if not member:
		member = discord.utils.find(lambda m: alternative.lower() in m.name.lower(), message.guild.members)
		print(f"using discord.py's find() with start strat: {member}")
	if not member:
		raise commands.MemberNotFound(alternative)
	return member


def parse_duration(duration: int):
	minutes, seconds = divmod(duration, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	weeks, wdays = divmod(days, 7)
	years, ydays = divmod(days, 365)
	months, mdays = divmod(ydays, 30)

	duration = []
	if years > 0:
		duration += [f'{years} years']
		if months > 0:
			duration += [f'{months} months']
		if mdays > 0:
			duration += [f'{mdays} days']
	elif months > 0:
		duration += [f'{months} months']
		if mdays > 0:
			duration += [f'{mdays} days']
	elif weeks > 0:
		duration += [f'{weeks} weeks']
		if wdays > 0:
			duration += [f'{wdays} days']
	elif days > 0:
		duration += [f'{days} days']
	if hours > 0:
		duration += [f'{hours} hours']
	if minutes > 0:
		duration += [f'{minutes} minutes']
	if seconds > 0:
		duration += [f'{seconds:1.3f} seconds']
	return ', '.join(duration)


def find_channel(context: Context, alternative):
	channel = None
	from discord import Message
	message: Message = context.message
	if message.channel_mentions:
		channel = message.channel_mentions[0]
		print(f"using mention {channel}")
	else:  # len(alternative) == len("564489099512381440"):
		try:
			channel = message.guild.get_channel(int(alternative))
		except ValueError:
			pass
		print(f"using id strat: {channel}")
	if not channel:
		try:
			channel = message.guild.get_channel(int(alternative[2:-1]))
		except ValueError:
			pass
		print(f"using alt id strat: {channel}")
	if not channel:
		channel = discord.utils.find(lambda m: m.name.lower().startswith(alternative.lower()), message.guild.channels)
		print(f"using discord.py's find() with start strat: {channel}")
	if not channel:
		channel = discord.utils.find(lambda m: alternative.lower() in m.name.lower(), message.guild.channels)
		print(f"using discord.py's find() with start strat: {channel}")
	if not channel:
		raise commands.ChannelNotFound(alternative)
	return channel


class BoolConverter(commands.Converter):
	def convert(self, ctx, argument):
		lookup = {
			True: ('yes', 'y', 'true', 't', '1', 'enable', 'on', "do"),
			False: ('no', 'n', 'false', 'f', '0', 'disable', 'off', "nay")
		}
		lower = argument.lower()
		for mode, storage in lookup.items():
			if lower in storage:
				return mode

		raise commands.BadArgument('whetever')
