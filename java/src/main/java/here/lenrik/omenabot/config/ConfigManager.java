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
	public static final GsonBuilder gBuilder;
	public static final Gson gson;
	public static Type serversType = new TypeToken<HashMap<String, ServerSettings>>() {}.getType();

	static {
		gBuilder = new GsonBuilder();
		gBuilder.setPrettyPrinting();
		gBuilder.disableHtmlEscaping();
		Adapters.register(gBuilder);
		gson = gBuilder.create();
	}

	public HashMap<String, ServerSettings> servers = new HashMap<>();
	public BotSettings botSettings = new BotSettings();
	public Responses responses = new Responses();
	private String saveLocation;

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
		OmenaBot.LOGGER.debug("saved configs here {}", location);
		try {
			BotSettings.save(location, botSettings, "private", "bot.json");
			Responses.save(location, responses, "responselists.json");
			Files.writeString(Path.of(location, "private", "servers.json"), gson.toJson(servers, serversType));
		} catch (IOException ioException) {
			OmenaBot.LOGGER.trace(ioException);
		}
	}

}
