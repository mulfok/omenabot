package here.lenrik.omenabot.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;

public class Responses {
	public ArrayList<String> trivia = new ArrayList<>();
	public ArrayList<String> _8ball = new ArrayList<>();
	public ArrayList<Joke> jokes = new ArrayList<>();
	public Hack hack = new Hack();
	public ArrayList<String> anime = new ArrayList<>();
	public ArrayList<String> f = new ArrayList<>();
	public HashMap<String, HashMap<String, String>> mc_commands = new HashMap<>();
	public ArrayList<String> pong_loss = new ArrayList<>();
	public ArrayList<String> pong_win = new ArrayList<>();

	public Responses () {
	}

	public static void save (String location, Responses config, String... next) throws IOException {
		String json = ConfigManager.gson.toJson(config) + "\n";
		Files.writeString(Path.of(location, next), json);
	}

	public static Responses load (String location) throws IOException {
		String json = Files.readString(Path.of(location));
		return ConfigManager.gson.fromJson(json, Responses.class);
	}

	public static class Joke {

		public final String joke;
		public final String punchline;
		public Joke (String joke_, String punchline_) {
			joke = joke_;
			punchline = punchline_;
		}

	}

	public static class Hack {
		public ArrayList<String> companies = new ArrayList<>();
		public ArrayList<String> payment = new ArrayList<>();
		public ArrayList<String> homework = new ArrayList<>();
		public ArrayList<String> mail_provider = new ArrayList<>();
		public ArrayList<ArrayList<String>> mail_body = new ArrayList<>();

	}

}
