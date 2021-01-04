package here.lenrik.omenabot.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;

import org.jetbrains.annotations.Nullable;

public class BotSettings {
	@SuppressWarnings("unused")
	public String token;
	@SuppressWarnings("unused")
	public HashMap<String, Boolean> ping;
	@SuppressWarnings("unused")
	public HashMap<String, Dev> devs;

	public static BotSettings load (String location) throws IOException {
		String json = Files.readString(Path.of(location));
		return ConfigManager.gson.fromJson(json, BotSettings.class);
	}

	public static class Dev {
		@SuppressWarnings("unused")
		public String name = "";
		@Nullable
		@SuppressWarnings("unused")
		public ArrayList<String> privileges;

		@Override
		public String toString () {
			return "{" + "name: \"" + name + '"' + ", privileges: " + privileges + "}";
		}

	}

}
