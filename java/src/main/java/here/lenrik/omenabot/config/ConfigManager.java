package here.lenrik.omenabot.config;

import here.lenrik.omenabot.OmenaBot;

import java.io.IOException;
import java.lang.reflect.Type;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.reflect.TypeToken;

public class ConfigManager {
	public static Type serversType = new TypeToken<HashMap<String, ServerSettings>>(){}.getType();
	public static final GsonBuilder gBuilder;
	public static final Gson gson;

	public HashMap<String, ServerSettings> servers = new HashMap<>();
	public BotSettings botSettings = new BotSettings();
	public Responses responses = new Responses();
	private String saveLocation;


	static {
		gBuilder = new GsonBuilder();
		gBuilder.setPrettyPrinting();
		gBuilder.registerTypeAdapter(Responses.Joke.class, new Adapters.Joke());
		gBuilder.registerTypeAdapter(BotSettings.Dev.class, new Adapters.Dev());
		gBuilder.registerTypeAdapter(BotSettings.class, new Adapters.BotSettings());
		gBuilder.registerTypeAdapter(ServerSettings.class, new Adapters.ServerSettings());
		gBuilder.registerTypeAdapter(serversType, new Adapters.Servers());
		gson = gBuilder.create();
	}

	public void load (String location) {
		saveLocation = location;
		try {
			botSettings = here.lenrik.omenabot.config.BotSettings.load(location + "/private/bot.json");
			responses = Responses.load(location + "/responselists.json");
			servers = gson.fromJson(Files.readString(Path.of(location, "/private/servers.json")), serversType);
		} catch (IOException e) {
			e.printStackTrace();
			saveLocation = null;
		}
	}

	public void save () {
		save(saveLocation);
	}

	public void save (String location) {
		OmenaBot.LOGGER.info(location);
		OmenaBot.LOGGER.info(gson.toJson(botSettings));
		Responses.save(location + "/responselists.json", responses);
		OmenaBot.LOGGER.info(gson.toJson(servers, serversType));
	}

}
