#!/usr/bin/python3.5
import discord
from discord.ext import commands
import asyncio
import os, stat
import json
import traceback
import re
import logging

loop = asyncio.get_event_loop()
home = os.getenv("HOME")
print("Home: '{0}'".format(home))
# all_ids = {}
# bridges = {}
# enabled_bridges = set()

# config = {}

# def __init__(bot: discord.ext.commands.Bot):
#     with open(home + "/chatbridge.json") as file:
#         self.config = json.load(file)
#         self.logger = logging.getLogger("bot.chat")
#         self.logger.info("Chatbridge initialization")

# def delete_caches():
#     for chan_id in self.all_ids:
#         self.all_ids[chan_id].bridgecache = None

# def set_bridge(bridge_id, chats):
#     delete_caches()
#     x = set()
#     for c in chats:
#         if not c in all_ids:
#             raise ValueError("Chat '{}' doesn't exist".format(c))
#         x.add(c)
#     self.bridges[bridge_id] = x

# def remove_bridge(bridge_id):
#     delete_caches()
#     disable_bridge(bridge_id)
#     if bridge_id in self.bridges:
#         del self.bridges[bridge_id]

# def enable_bridge(bridge_id):
#     delete_caches()
#     loop.create_task(update_discord_topics())
#     if bridge_id in self.bridges:
#         self.enabled_bridges.add(bridge_id)
#     else:
#         raise ValueError("Bridge '{}' does not exist".format(bridge_id))

# def disable_bridge(bridge_id):
#     delete_caches()
#     loop.create_task(update_discord_topics())
#     if bridge_id in self.enabled_bridges:
#         self.enabled_bridges.remove(bridge_id)
#     else:
#         raise ValueError("Bridge '{}' does not exist".format(bridge_id))

# def add_chat(channel):
#     delete_caches()
#     channel_id = channel.get_id()
#     if channel_id in self.all_ids:
#         raise ValueError("Chat '{}' already exists".format(channel_id))
#     else:
#         self.all_ids[channel_id] = channel

# def delete_chat(channel_id):
#     delete_caches()
#     if channel_id in self.all_ids:
#         del self.all_ids[channel_id]
#     for x in self.bridges:
#         if channel_id in x:
#             x.remove(channel_id)

# def get_chat_by_id(chat_id):
#     if chat_id in self.all_ids:
#         return self.all_ids[chat_id]
#     else:
#         return None

# def extract_discord_id(server, string):
#     if string[0:2] == "<#" and string[-1] == ">":
#         return string[2:-1]
#     elif string[0] == "#":
#         for channel in server.channels:
#             if "#" + channel.name == string:
#                 return channel.id
#     else:
#         return None

# def extract_minecraft_id(string):
#     if get_socket_path(string):
#         return string
#     else:
#         return None

# def extract_id(server, string):
#     dis_id = extract_discord_id(server, string)
#     if dis_id != None:
#         return dis_id
#     min_id = extract_minecraft_id(string)
#     if min_id != None:
#         return min_id
#     return None

# def get_socket_path(minecraft_server):
#     path = "{0}/minecraft-servers/{1}/servercli".format(home, minecraft_server)
#     try:
#         mode = os.stat(path).st_mode
#     except FileNotFoundError:
#         return None
#     if stat.S_ISSOCK(mode) != 0:
#         return path
#     return None

# def connect_chat(discord_server, string):
#     discord_id = extract_discord_id(discord_server, string)
#     for channel in discord_server.channels:
#         if channel.id == discord_id or channel.name == discord_id:
#             print("Added Discord chat {}".format(channel.name))
#             add_chat(DiscordChat(channel))
#             return
#     minecraft_id = extract_minecraft_id(string)
#     if minecraft_id != None:
#         print("Added Minecraft chat {}".format(minecraft_id))
#         add_chat(MinecraftChat(minecraft_id))
#         return
#     raise ValueError("Couldn't find chat {}".format(string))

# def bridge_all(discord_server, bridge_id, strings, enabled=True):
#     chat_ids = set()
#     for string_id in strings:
#         clean_id = extract_id(discord_server, string_id)
#         if clean_id == None:
#             raise ValueError(
#                 "Discord channel or Minecraft server not found: {}".format(
#                     string_id
#                 )
#             )
#         else:
#             chat_ids.add(clean_id)
#             if get_chat_by_id(clean_id) == None:
#                 connect_chat(discord_server, string_id)
#     set_bridge(bridge_id, chat_ids)
#     if enabled:
#         enable_bridge(bridge_id)

# generalInfo = re.compile("^\[\d\d:\d\d:\d\d\] \[Server thread/INFO\]: (.*)")
# message_match = re.compile("^<(§\w)?((\w)+)(§\w)?> (.*)$")
# joined_match = re.compile("^(§\w)?((\w)+)(§\w)? joined the game")
# left_match = re.compile("^(§\w)?((\w)+)(§\w)? left the game")
# count_match = re.compile("^There are (\d*)/\d* players online:")
# list_1_13_match = re.compile("^There are (\d*) of a max \d* players online: (.*)")

# def extract_message(string):
#     match = message_match.fullmatch(generalInfo.fullmatch(string))
#     if match:
#         user = match.group(2)
#         message = match.group(5)
#         return (user, message)
#     return None

# def extract_joined(string):
#     match = joined_match.fullmatch(generalInfo.fullmatch(string))
#     if match:
#         return match.group(2)
#     return None

# def extract_left(string):
#     match = left_match.fullmatch(generalInfo.fullmatch(string))
#     if match:
#         return match.group(2)
#     return None

# def extract_playercount(string):
#     match = count_match.fullmatch(generalInfo.fullmatch(string))
#     if match:
#         count = match.group(1)
#         return int(count)
#     return None

# def extract_info(string):
#     match = generalInfo.fullmatch(string)
#     if match:
#         return match.group(1)
#     return None

# def extract_1_13_list(string):
#     match = list_1_13_match.fullmatch(generalInfo.fullmatch(string))
#     if match:
#         return (int(match.group(1)), match.group(2))
#     return None

# def escape_tellraw(string):
#     assert isinstance(string, str)
#     cleanup = string.replace("§", "")
#     return json.dumps(cleanup)

# class Chat:
#     def __init__(self):
#         self.bridgecache = None

#     def get_id(self):
#         pass

#     def get_short_name(self):
#         return self.get_id()

#     def get_long_name(self):
#         return self.get_short_name()

#     def send_message(self, sender_name, sender_channel, message):
#         pass

#     def send_text(self, text):
#         pass

#     def send_joined_message(self, who, channel):
#         pass

#     def send_left_message(self, who, channel):
#         pass

#     # def send_greeting(self):
#     # 	self.send_text("Hi, I'm a Minecraft <-> Discord chat bridge.\n" + \
#     # 				f"* to learn about commands type `!chat help`")

#     def set_private(self, is_private):
#         raise ValueError("This is only available ingame")

#     def bridged_channels(self):
#         if self.bridgecache != None:
#             return self.bridgecache
#         myid = self.get_id()
#         channels = set()
#         for bridge_id in enabled_bridges:
#             bridge = bridges[bridge_id]
#             if myid in bridge:
#                 for channel_id in bridge:
#                     if channel_id != myid:
#                         channels.add(channel_id)
#         self.bridgecache = []
#         for channel_id in channels:
#             self.bridgecache.append(all_ids[channel_id])
#         return self.bridgecache

#     def list_players(self):
#         playerlist = get_playerlist_for_channel(self)
#         self.send_text(playerlist)

#     def list_bridges(self):
#         bridge_desc = []
#         for bridge_id, bridge in bridges.items():
#             enabled_str = "enabled" if bridge_id in enabled_bridges else "disabled"
#             channel_names = []
#             for channel_id in bridge:
#                 channel = all_ids[channel_id]
#                 channel_names.append(channel.get_long_name())
#             bridge_desc.append(
#                 "* {}: ({}) - {}".format(
#                     bridge_id, " ,".join(channel_names), enabled_str
#                 )
#             )
#         message = "Available channels:\n" + "\n".join(bridge_desc)
#         self.send_text(message)

#     def handle_command(self, sender_name, message):
#         tokens = message.split(" ")
#         if tokens[0] == "!chat":
#             if tokens[1] == "help":
#                 self.send_text(
#                     "Minecraft <-> Discord chat bridge help:\n"
#                     + "* Commands: \n"
#                     + "* !chat help\n"
#                     + "* !chat list\n"
#                     + "* !chat channels\n"
#                     + "* !chat enable/disable <name>\n"
#                     + "* !chat private - others only see messages with prefix '!!'\n"
#                     + "* !chat public - others see all messages"
#                 )
#             elif tokens[1] == "list":
#                 self.list_players()
#             elif tokens[1] == "channels":
#                 self.list_bridges()
#             elif tokens[1] == "enable":
#                 enable_bridge(tokens[2])
#                 self.broadcast_text("Enabled channel {}".format(tokens[2]))
#             elif tokens[1] == "disable":
#                 self.broadcast_text("Disabling channel {}".format(tokens[2]))
#                 disable_bridge(tokens[2])
#             elif tokens[1] == "private":
#                 self.set_private(True)
#             elif tokens[1] == "public":
#                 self.set_private(False)

#     def emit_message(self, sender_name, message):
#         isprefixed = len(message) > 2 and message[0:2] == "!!"
#         if message[0] == "!" and not isprefixed:
#             try:
#                 self.handle_command(sender_name, message)
#             except IndexError as e:
#                 self.send_text("Error: Not enough arguments")
#             except ValueError as e:
#                 self.send_text("Error: " + str(e))
#             except Exception as e:
#                 traceback.print_exc()
#                 self.send_text("Error: " + str(e))
#         else:
#             if isprefixed:
#                 message = message[2:]
#             for channel in self.bridged_channels():
#                 channel.send_message(sender_name, self, message)

#     def emit_joined(self, name):
#         for channel in self.bridged_channels():
#             channel.send_joined_message(name, self)

#     def emit_left(self, name):
#         for channel in self.bridged_channels():
#             channel.send_left_message(name, self)

#     def broadcast_text(self, text):
#         for channel in [self] + self.bridged_channels():
#             channel.send_text(text)

# class DiscordChat(Chat):
#     def __init__(self, discord_channel):
#         super().__init__()
#         self.discord_channel = discord_channel
#         # self.send_greeting()

#     def get_id(self):
#         return self.discord_channel.id

#     def get_short_name(self):
#         return "discord"

#     def get_long_name(self):
#         return "#" + self.discord_channel.name

#     async def send_message_raw(self, message):
#         try:
#             await client.send_message(self.discord_channel, message)
#         except:
#             traceback.print_exc()
#             print("Failed to send message on discord")

#     def send_text(self, text):
#         loop.create_task(self.send_message_raw(text))

#     def send_message(self, sender_name, sender_channel, message):
#         channel_name = sender_channel.get_short_name()
#         msg = "**<{0}@{1}>:** {2}".format(sender_name, channel_name, message)
#         self.send_text(msg)

#     def send_joined_message(self, who, channel):
#         channel_name = channel.get_short_name()
#         msg = "**_{0} joined {1}_**".format(who, channel_name)
#         self.send_text(msg)

#     def send_left_message(self, who, channel):
#         channel_name = channel.get_short_name()
#         msg = "**_{0} left {1}_**".format(who, channel_name)
#         self.send_text(msg)

#     async def set_topic(self, topic):
#         await client.edit_channel(self.discord_channel, topic=topic)

# class MinecraftChat(Chat):
#     def __init__(self, server_name):
#         super().__init__()
#         self.server_name = server_name
#         self.private = False
#         self.connecting = False
#         self.read_task = None
#         self.player_count = 0
#         self.player_list = ""
#         self.reconnect()

#     def get_id(self):
#         return self.server_name

#     def reconnect(self):
#         if not self.connecting:
#             print("Connecting to {}".format(self.get_short_name()))
#             self.reader = None
#             self.writer = None
#             self.read_task = None
#             self.connecting = True
#             loop.create_task(self.connect(self.server_name))
#         else:
#             print("Already trying to connect to {}".format(self.get_short_name()))

#     async def connect(self, server_name):
#         wait = 5
#         while True:
#             try:
#                 path = get_socket_path(server_name)
#                 self.reader, self.writer = await asyncio.open_unix_connection(path)
#                 print("Connected to Minecraft server {0}".format(server_name))
#                 self.connecting = False
#                 self.send_greeting()
#                 self.read_task = loop.create_task(self.read_chat())
#                 return
#             except:
#                 traceback.print_exc()
#                 print(
#                     "Could not connect to Minecraft server '{0}', path '{1}'".format(
#                         server_name, path
#                     )
#                 )
#                 await asyncio.sleep(wait)
#                 wait += 5
#                 if wait > 60:
#                     wait = 60

#     def send_raw_command(self, message):
#         loop.create_task(self.send_raw_async(message))

#     async def send_raw_async(self, message):
#         encoded = message.encode()
#         try:
#             self.writer.write(encoded)
#             self.writer.write(b"\n")
#             await self.writer.drain()
#         except:
#             traceback.print_exc()
#             self.reconnect()

#     def send_text(self, text):
#         text_esc = escape_tellraw(text)
#         command = '/tellraw @a ["",{"text":' + text_esc + ',"color":"gray"}]'
#         self.send_raw_command(command)

#     def send_message(self, sender_name, sender_channel, message):
#         channel_name = sender_channel.get_short_name()
#         sender_esc = escape_tellraw(sender_name)
#         channel_esc = escape_tellraw(channel_name)
#         message_esc = escape_tellraw(message)
#         command = (
#             '/tellraw @a ["",{"text":"<","color":"white"},{"text":'
#             + sender_esc
#             + ',"color":"white"},{"text":"@","color":"gray"},{"text":'
#             + channel_esc
#             + ',"color":"gray"},{"text":"> ","color":"white"},{"text":'
#             + message_esc
#             + ',"color":"none"}]'
#         )
#         self.send_raw_command(command)

#     def send_joined_message(self, who, channel):
#         channel_name = channel.get_short_name()
#         who_esc = escape_tellraw(who)
#         channel_esc = escape_tellraw(channel_name)
#         command = (
#             '/tellraw @a ["",{"text":'
#             + who_esc
#             + ',"color":"yellow"},{"text":" joined ","color":"yellow"},{"text":'
#             + channel_esc
#             + ',"color":"yellow"}]'
#         )
#         self.send_raw_command(command)

#     def send_left_message(self, who, channel):
#         channel_name = channel.get_short_name()
#         who_esc = escape_tellraw(who)
#         channel_esc = escape_tellraw(channel_name)
#         command = (
#             '/tellraw @a ["",{"text":'
#             + who_esc
#             + ',"color":"yellow"},{"text":" left ","color":"yellow"},{"text":'
#             + channel_esc
#             + ',"color":"yellow"}]'
#         )
#         self.send_raw_command(command)

#     def set_private(self, is_private):
#         self.send_text(
#             "Chat is now private. Prefix messages with !!"
#             if is_private
#             else "Chat is now public"
#         )
#         self.private = is_private
#         loop.create_task(update_discord_topics())

#     def emit_message(self, sender_name, message):
#         if not self.private or (len(message) > 0 and message[0] == "!"):
#             super().emit_message(sender_name, message)
#         else:
#             return

#     def emit_joined(self, name):
#         if not self.private:
#             super().emit_joined(name)

#     def emit_left(self, name):
#         if not self.private:
#             super().emit_left(name)

#     def request_list(self):
#         self.send_raw_command("/list")

#     async def read_chat(self):
#         try:
#             print("Start reading from {}".format(self.get_id()))
#             self.request_list()
#             awaiting_list = False
#             while self.reader != None:
#                 msg = await self.reader.readline()
#                 if len(msg) == 0:
#                     raise ValueError("Probably disconnected")
#                 if msg:
#                     msg_str = msg.decode()[:-1]
#                     print(msg_str)
#                     normal_message = extract_message(msg_str)
#                     if awaiting_list:
#                         awaiting_list = False
#                         player_list = extract_info(msg_str)
#                         if player_list != None:
#                             self.player_list = player_list
#                             loop.create_task(update_discord_topics())
#                             continue
#                         else:
#                             print("Weird, didn't get a player list")
#                     if normal_message != None:
#                         self.emit_message(normal_message[0], normal_message[1])
#                         continue
#                     joined = extract_joined(msg_str)
#                     if joined != None:
#                         self.request_list()
#                         self.emit_joined(joined)
#                         continue
#                     left = extract_left(msg_str)
#                     if left != None:
#                         self.request_list()
#                         self.emit_left(left)
#                         continue
#                     count = extract_playercount(msg_str)
#                     if count != None:
#                         self.player_count = count
#                         awaiting_list = True
#                         continue
#                     list_1_13 = extract_1_13_list(msg_str)
#                     if list_1_13 != None:
#                         self.player_count, self.player_list = list_1_13
#                         loop.create_task(update_discord_topics())
#                         continue
#         except:
#             traceback.print_exc()
#             print("Disconnected from Minecraft server {}".format(self.server_name))
#             self.reader = None
#             if self.writer:
#                 self.writer.close()
#             self.writer = None
#             self.reconnect()
#             return
#         finally:
#             self.read_task = None

# def get_playerlist_for_channel(chat):
#     other_chats = chat.bridged_channels()
#     if len(other_chats) == 0:
#         return "All chats disabled. To enable the chat use '!chat channels' and '!chat enable <name>'"
#     connected_chats = [chat] + other_chats
#     total = 0
#     counts = []
#     lists = []
#     for minecraft_chat in connected_chats:
#         if isinstance(minecraft_chat, MinecraftChat):
#             count = minecraft_chat.player_count
#             total += count
#             name = minecraft_chat.get_short_name()
#             counts.append("{}: {}".format(name, count))
#             if count > 0:
#                 if minecraft_chat.private:
#                     lists.append("* {}: (private chat)".format(name))
#                 else:
#                     players = minecraft_chat.player_list
#                     lists.append("* {}: {}".format(name, players))
#     return (
#         "{} {} online (".format(total, "Player" if total == 1 else "Players")
#         + ", ".join(counts)
#         + ") \n"
#         + "\n".join(lists)
#     )

# async def update_discord_topics():
#     for dchatid, discord_chat in all_ids.items():
#         if isinstance(discord_chat, DiscordChat):
#             try:
#                 topic = get_playerlist_for_channel(discord_chat)
#                 print(
#                     "Setting topic of channel channel {} to '{}'".format(
#                         discord_chat.get_short_name(), topic
#                     )
#                 )
#                 await discord_chat.set_topic(topic)
#             except:
#                 traceback.print_exc()

# @client.event
# async def on_ready():
#     print("Logged in as")
#     print(client.user.name)
#     print(client.user.id)
#     print("------")
#     for server in client.servers:
#         for bridge in config["bridges"]:
#             name = bridge["name"]
#             bridge_all(server, name, bridge["channels"], enabled=bridge["enabled"])
#         break

# @client.event
# async def on_message(message):
#     chanid = message.channel.id
#     if message.author.id == client.user.id:
#         return
#     words = message.content.split(" ")
#     try:
#         reply = ""
#         if words[0] == "!bridge":
#             if not message.author.server_permissions.manage_server:
#                 await client.send_message(
#                     "You don't have 'manage_server' permissions"
#                 )
#                 return
#             if len(words) < 2:
#                 raise ValueError("Usage: !bridge add/del/enable/disable [...]")
#             if words[1] == "add":
#                 if len(words) < 5:
#                     raise ValueError(
#                         "Usage: !bridge add <brige_name> <chat1> <chat2> [...]"
#                     )
#                 bridge_all(message.server, words[2], words[3:])
#                 reply = "chat bridge '{}' created".format(words[2])
#                 loop.create_task(update_discord_topics())
#             await client.send_message(message.channel, reply)
#             return
#     except Exception as e:
#         await client.send_message(message.channel, str(e))
#         raise

#     print("Chat: {}".format(message.channel.id))
#     chat = get_chat_by_id(chanid)
#     if chat != None:
#         chat.emit_message(message.author.display_name, message.clean_content)
#     return


class Cog(commands.Cog):
	def __init__(seld,  bot: discord.ext.commands.Bot):
		self.bot = bot
	
	@self.bot.event
	async def on_socket_raw_receive(msg):
		print(msg)
