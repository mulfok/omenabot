import json, os


class Data:
	def __init__(self, directory):
		self.profiles = {}
		self.save_dir = directory
		# with open(self.save_dir / 'private' / 'servers.json') as servers_file:
		# 	self.servers = json.load(servers_file)

		# with open(self.save_dir / 'private' / 'dnd.json') as servers_file:
		# 	self.dnd_conf = json.load(servers_file)

		with open(self.save_dir / 'private' / 'bot.json') as file:
			self.bot = json.load(file)

		with open(self.save_dir / 'private' / 'tokens.json') as file:
			self.tokens = json.load(file)

		with open(self.save_dir / "responselists.json") as file:
			self.responses = json.load(file)

		self.prof_dir = self.save_dir / 'private' / 'profiles'
		if not os.path.exists(self.prof_dir):
			os.mkdir(self.prof_dir)
		for file in os.listdir(self.prof_dir):
			with open(self.prof_dir.joinpath(file)) as prof_file:
				self.profiles[file[0:-5]] = json.load(prof_file)

	def save_server(self, id: int):
		gid = f"{id}.json"
		with open(self.prof_dir / gid, "w") as serv_file:
			json.dump(self.profiles[gid[0:-5]], serv_file, indent=2)
