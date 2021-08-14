import asyncio
import random

import discord
from discord.ext import commands

from omenabot import OmenaBot


class Fun(commands.Cog):
	def __init__(self, bot: OmenaBot):
		self.bot = bot

	@commands.Cog.listener("on_message")
	async def on_message(self, message: discord.Message):
		if "who is an idiot?" in message.content and f'{message.author.id}' in self.bot.data.bot['devs']:
			emoji = random.choice(random.choice([
				[
					'<:silove:866053322132815893>',
					'<:siblue:856960614748782613>',
					"<:kekw:784381728302170112>"
				],
				[f"<:silove{num}:{eid}>" for num, eid in enumerate(
					"866053322023895040 866053322308583434 866053322551853056 866053322070032394 "
					"866053322452107274 866053322048667668 866053322096115724 866053321667117077 "
					"866053322648715274 866053321982345216 866053321948528710 866053322145136660 "
					"866053322082746429 866053321910124554 866053321894395914 866053322002923540 "
					"866053322070294578 866053322142253117 866053322041589830 866053322061774918 "
					"866053321689530449 866053321919037460 866053322050240513 866053321906716673".split(" "))]
			]))
			await message.channel.send(f"<@{message.author.id}>, you are an idiot {emoji}")

	@commands.Cog.listener("on_member_leave")
	async def on_member_leave(self, member):
		await asyncio.sleep(random.gammavariate(1.6, 0.8) * 2)
		if "channels" in self.bot.data.profiles[f'{member.guild.id}'] and "welcomes" in self.bot.data.profiles[f'{member.guild.id}'][
			"channels"]:
			await member.guild.get_channel(int(self.bot.data.profiles[f'{member.guild.id}']["channels"]["welcomes"])).send(
				random.choice(self.bot.data.responses["bye"]).format(member))
		elif member.guild.system_channel:
			await member.guild.system_channel.send(random.choice(self.bot.data.responses["bye"]).format(member))

	@commands.Cog.listener("on_member_join")
	async def on_member_join(self, member):
		await asyncio.sleep(random.gammavariate(1.6, 0.8) * 2)
		self.bot.data.profiles[f'{member.guild.id}'].setdefault("channels", {})
		if "welcomes" in self.bot.data.profiles[f'{member.guild.id}']["channels"]:
			await member.guild.get_channel(int(self.bot.data.profiles[f'{member.guild.id}']["channels"]["welcomes"])).send(
				random.choice(self.bot.data.responses["hello"]).format(member))
		elif member.guild.system_channel:
			await member.guild.system_channel.send(random.choice(self.bot.data.responses["hello"]).format(member))

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# easter egg commands
	# alcohol command
	@commands.command(hidden=True)
	async def alcohol(self, context):
		if context.author.id == 397573419811602442:  # karnage 397573419811602442
			await context.send("Go drink alcohol you madman. :beer:")
		else:
			await context.send("This command isn't for you! :x:")

	# coffee command
	@commands.command(hidden=True)
	async def coffee(self, context):
		if context.author.id == 721045183982207046:  # lenrik 721045183982207046
			await context.send("Go drink coffee you madman. :coffee:")

		else:
			await context.send("This command isn't for you! :x:")

	# ifstatment command
	@commands.command(name="if", hidden=True)
	async def _if(self, context):
		if context.author.id == 465816879072542720:
			await context.send("Go learn if statments you madman. :dagger:")

		else:
			await context.send("This command isn't for you! :x:")

	# hack command
	@commands.command(hidden=True)
	async def hack(self, context: discord.ext.commands.Context, *, hackvic):
		message: discord.Message = context.message
		# store homework amount in temp variable
		homeworkstorage = random.choice(self.bot.data.responses["hack"]["homework"])
		# send messages in a timely order
		hack_message = await context.send(f"Hacking {hackvic}...")
		await asyncio.gather(asyncio.sleep(2), message.delete())
		await hack_message.edit(content=f"Grabbing {homeworkstorage} 'Homework' folder...")
		await asyncio.sleep(2)
		await hack_message.edit(content=f'Selling data to {random.choice(self.bot.data.responses["hack"]["companies"])}...')
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Payment recieved: {random.choice(self.bot.data.responses['hack']['payment'])}")
		await asyncio.sleep(2)
		await hack_message.edit(content="Bypassing Discord security...")
		await asyncio.sleep(2)
		mail_before, mail_after = random.choice(self.bot.data.responses['hack']['mail_body'])
		await hack_message.edit(
			content=f"Email: {mail_before}{hackvic}{mail_after}@{random.choice(self.bot.data.responses['hack']['mail_provider'])}"
			        f"\nPassword: ihateyouihateyougodie")
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Reporting {hackvic} for breaking Discord TOS...")
		await asyncio.sleep(2)
		await hack_message.edit(content=f"Laughing evilly...")
		await asyncio.sleep(2)
		await context.send(f"The 100% real hack of {hackvic} is complete.")
		await context.send(f"Homework folder size: {homeworkstorage}")

	@commands.command(hidden=True)
	async def slap(self, context, *, person: discord.User):
		await context.send(f"Slapped {person}!")

	# joke command
	@commands.command(name="joke", brief="…tells a joke.", help="Blame <@465816879072542720> for it's all his fault")
	async def joke(self, context):
		joke_line, punchline = random.choice(self.bot.data.responses["jokes"])
		message = await context.send(joke_line)
		await asyncio.sleep(2)
		await message.edit(content=joke_line + "\n" + punchline)




def setup(bot: OmenaBot):
	bot.add_cog(Fun(bot))
