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
		return ConfigManager.gson.fromJson(Files.readString(Path.of(location)), BotSettings.class);
	}

	public static void save (String fisrst, BotSettings settings, String... next) throws IOException {
		Files.writeString(Path.of(fisrst, next), ConfigManager.gson.toJson(settings));
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
