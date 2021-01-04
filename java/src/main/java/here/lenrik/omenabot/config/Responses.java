package here.lenrik.omenabot.config;

import here.lenrik.omenabot.OmenaBot;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;

public class Responses {
	@SuppressWarnings("unused")
	public HashMap<String, HashMap<String, String>> mc_commands = new HashMap<>();
	@SuppressWarnings({"unused", "rawtypes"})
	public HashMap<String, ArrayList> hack = new HashMap<>();
	@SuppressWarnings("unused")
	public ArrayList<String> pong_loss = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<String> pong_win = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<String> trivia = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<String> anime = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<String> _8ball = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<Joke> jokes = new ArrayList<>();
	@SuppressWarnings("unused")
	public ArrayList<String> f = new ArrayList<>();

	public Responses () {
	}

	public static void save (String location, Responses config) {
		String json = ConfigManager.gson.toJson(config);
		OmenaBot.LOGGER.info(json);
		try {
			Files.writeString(Path.of(location), json);
		} catch (IOException e) {
			OmenaBot.LOGGER.trace(e);
		}
	}

	public static class Joke {

		public Joke (String joke_, String punchline_) {
			joke = joke_;
			punchline = punchline_;
		}

		public final String joke;
		public final String punchline;

	}

	public static Responses load (String location) throws IOException {
		String json = Files.readString(Path.of(location));
		return ConfigManager.gson.fromJson(json, Responses.class);
	}

}
