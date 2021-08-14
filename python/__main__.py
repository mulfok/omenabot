import argparse
import sys

from omenabot import OmenaBot

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="OmenaBot cli.")
	parser.add_argument("--token-name", default=["omena"], help="Bot token name in config.", nargs="+")
	parser.add_argument("--gui", help="enable gui", action="store_true")
	parser.add_argument("--no-load", default=["gui"], metavar="module", help="extensions that should not be loaded", nargs="+")
	parser.add_argument("--debug", help="enable debug", action="store_true")
	args = parser.parse_args(sys.argv[1:])
	print(args)
	bot = OmenaBot(" ".join(args.token_name), no_load=args.no_load, gui=args.gui, debug=args.debug)
	bot.run_bot(bot.run)
