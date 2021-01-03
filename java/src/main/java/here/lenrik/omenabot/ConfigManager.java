package here.lenrik.omenabot;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

import static here.lenrik.omenabot.ConfigManager.Adapters.*;

public class ConfigManager {
	public static final GsonBuilder gBuilder;
	public static final Gson gson;

	public ServersSettings servers = new ServersSettings();
	public BotSettings botSettings = new BotSettings();
	public Responses responses = new Responses();
	private String saveLocation;


	static {
		gBuilder = new GsonBuilder();
		gBuilder.registerTypeAdapter(Responses.Joke.class, new JokeAdapter());
		gBuilder.registerTypeAdapter(BotSettings.Dev.class, new DevAdapter());
		gBuilder.registerTypeAdapter(BotSettings.class, new BotSettingsAdapter());
		gBuilder.registerTypeAdapter(ServerSettings.class, new ServerSettingsAdapter());
		gBuilder.registerTypeAdapter(ServersSettings.class, new ServersSettingsAdapter());
		gson = gBuilder.create();
	}

	@SuppressWarnings({"unchecked"})
	public void load (String location) {
		saveLocation = location;
		try {
			botSettings = BotSettings.load(location + "/private/bot.json");
			responses = Responses.load(location + "/responselists.json");
			servers = gson.fromJson(Files.readString(Path.of(location, "/private/servers.json")), ServersSettings.class);
		} catch (IOException e) {
			e.printStackTrace();
			saveLocation = null;
		}
	}

	public void save () {
		save(saveLocation);
	}

	private void save (String location) {

	}

	public static class BotSettings {
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

	public static class ServersSettings extends HashMap<String, ServerSettings> {

	}

	public static class Responses {
		@SuppressWarnings("unused")
		public HashMap<String, HashMap<String, String>> mc_commands = new HashMap<>();
		@SuppressWarnings("unused")
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

		public static class Joke {

			Joke (String joke_, String punchline_) {
				joke = joke_;
				punchline = punchline_;
			}

			public String joke;
			public String punchline;

		}

		public static Responses load (String location) throws IOException {
			String json = Files.readString(Path.of(location));
			return ConfigManager.gson.fromJson(json, Responses.class);
		}

	}

	public static class ServerSettings {
		@Nullable
		@SuppressWarnings("unused")
		public String name;
		@NotNull
		public String prefix = "~";
		@SuppressWarnings("unused")
		public HashMap<String, String> nicks;
		@SuppressWarnings("unused")
		public HashMap<String, Id_s> channels;

		public static class Id_s {
			@NotNull Long id;
			@Nullable ArrayList<Long> ids;

			public Id_s (@NotNull Long id, @Nullable ArrayList<Long> ids) {
				this.id = id;
				this.ids = ids;
			}

			public static Id_s valueOf (ArrayList<Long> ids) {
				return new Id_s(ids.get(0), ids);
			}

			public Object get () {
				return ids == null ? id : ids;
			}

			public static Id_s valueOf (Long value) {
				return new Id_s(value, null);
			}

			@Override
			public String toString () {
				return ids == null ? id.toString() : ids.toString();
			}

		}

		@Override
		public String toString () {
			return name + "{prefix='" + prefix + "'" + (nicks != null ? ", nicks:" + nicks : "") + (channels != null ? ", channels:" + channels : "") + "}";
		}

	}

	public static final class Adapters{

		public static final class ServersSettingsAdapter extends TypeAdapter<ServersSettings> {

			@Override
			public void write (JsonWriter out, ServersSettings servers) throws IOException {
				if (servers == null) {
					out.nullValue();
					return;
				}
				out.beginObject();
				for (Map.Entry<String, ServerSettings> server : servers.entrySet()) {
					out.name(server.getKey());
					out.jsonValue(gson.toJson(server.getValue()));
				}
				out.endObject();
			}

			@Override
			public ServersSettings read (JsonReader reader) throws IOException {
				var servers = new ServersSettings();
				reader.beginObject();
				while (reader.hasNext()) {
					reader.peek();
					servers.put(reader.nextName(), gson.getAdapter(ServerSettings.class).read(reader));
				}
				reader.endObject();
				return servers;
			}

		}

		public static final class ServerSettingsAdapter extends TypeAdapter<ServerSettings> {

			@Override
			public void write (JsonWriter out, ServerSettings settings) throws IOException {
				if (settings == null) {
					out.nullValue();
					return;
				}
				out.beginObject();
				out.name("name");
				out.value(settings.name);
				out.name("prefix");
				out.value(settings.prefix);
				if (settings.nicks != null) {
					out.name("nicks");
					out.beginObject();
					for (var nick : settings.nicks.entrySet()) {
						out.name(nick.getKey());
						out.value(nick.getValue());
					}
					out.endObject();
				}
				if (settings.channels != null) {
					out.name("channels");
					out.beginObject();
					for (var channel : settings.channels.entrySet()) {
						out.name(channel.getKey());
						ServerSettings.Id_s id_s = channel.getValue();
						if (id_s.get() instanceof Long) {
							out.value((Long) id_s.get());
						} else {
							out.beginArray();
							//noinspection unchecked
							for (Long id : (ArrayList<Long>) id_s.get()) {
								out.value(id);
							}
							out.endArray();
						}
					}
					out.endObject();
				}
				out.endObject();
			}

			@Override
			public ServerSettings read (JsonReader reader) throws IOException {
				ServerSettings settings = new ServerSettings();
				reader.beginObject();
				String fieldname = null;

				while (reader.hasNext()) {
					JsonToken token = reader.peek();

					if (token.equals(JsonToken.NAME)) {
						//get the current token
						fieldname = reader.nextName();
					}

					if ("name".equals(fieldname)) {
						//move to next token
						token = reader.peek();
						settings.name = reader.nextString();
					}

					if ("prefix".equals(fieldname)) {
						//move to next token
						token = reader.peek();
						settings.prefix = reader.nextString();
					}

					if ("nicks".equals(fieldname)) {
						settings.nicks = new HashMap<>();
						reader.beginObject();
						while (reader.hasNext()) {
							settings.nicks.put(reader.nextName(), reader.nextString());
						}
						reader.endObject();
					}

					if ("channels".equals(fieldname)) {
						settings.channels = new HashMap<>();
						reader.beginObject();
						while (reader.hasNext()) {
							String channel = reader.nextName();
							token = reader.peek();
							if (token.equals(JsonToken.BEGIN_ARRAY)) {
								ArrayList<Long> ids = new ArrayList<>();
								reader.beginArray();
								while (reader.hasNext()) {
									ids.add(reader.nextLong());
								}
								reader.endArray();
								settings.channels.put(channel, ServerSettings.Id_s.valueOf(ids));
							} else {
								settings.channels.put(channel, ServerSettings.Id_s.valueOf(reader.nextLong()));
							}
						}
						reader.endObject();
					}
				}
				reader.endObject();
				return settings;
			}

		}

		public static final class BotSettingsAdapter extends TypeAdapter<BotSettings> {

			@Override
			public void write (JsonWriter out, BotSettings settings) throws IOException {
				if (settings == null) {
					out.nullValue();
					return;
				}
				out.beginObject();
				out.name("token");
				out.value(settings.token);
				if (settings.devs != null) {
					out.name("devs");
					out.beginObject();
					for (var dev : settings.devs.entrySet()) {
						out.name(dev.getKey());
						out.jsonValue(gson.toJson(dev.getValue()));
					}
					out.endObject();
				}
				if (settings.ping != null) {
					out.name("ping");
					out.beginObject();
					for (var entry : settings.ping.entrySet()) {
						out.name(entry.getKey());
						out.value(entry.getValue());
					}
					out.endObject();
				}
				out.endObject();

			}

			@Override
			public BotSettings read (JsonReader reader) throws IOException {
				BotSettings settings = new BotSettings();
				reader.beginObject();
				String fieldname = null;

				while (reader.hasNext()) {
					JsonToken token = reader.peek();

					if (token.equals(JsonToken.NAME)) {
						//get the current token
						fieldname = reader.nextName();
					}

					if ("token".equals(fieldname)) {
						//move to next token
						token = reader.peek();
						settings.token = reader.nextString();
					}

					if ("devs".equals(fieldname)) {
						settings.devs = new HashMap<>();
						reader.beginObject();
						while (reader.hasNext()) {
							settings.devs.put(reader.nextName(), gson.getAdapter(BotSettings.Dev.class).read(reader));
						}
						reader.endObject();
					}

					if ("ping".equals(fieldname)) {
						settings.ping = new HashMap<>();
						reader.beginObject();
						while (reader.hasNext()) {
							settings.ping.put(reader.nextName(), reader.nextBoolean());
						}
						reader.endObject();
					}
				}
				reader.endObject();
				return settings;
			}

		}

		public static final class DevAdapter extends TypeAdapter<BotSettings.Dev> {

			@Override
			public void write (JsonWriter out, BotSettings.Dev settings) throws IOException {
				if (settings == null) {
					out.nullValue();
					return;
				}
				out.beginObject();
				out.name("name");
				out.value(settings.name);
				if (settings.privileges != null) {
					out.name("privileges");
					out.beginArray();
					for (String privilege : settings.privileges) {
						out.value(privilege);
					}
					out.endArray();
				}
				out.endObject();
			}

			@Override
			public BotSettings.Dev read (JsonReader reader) throws IOException {
				BotSettings.Dev dev = new BotSettings.Dev();
				reader.beginObject();
				String fieldname = null;

				while (reader.hasNext()) {
					JsonToken token = reader.peek();

					if (token.equals(JsonToken.NAME)) {
						//get the current token
						fieldname = reader.nextName();
					}

					if ("name".equals(fieldname)) {
						//move to next token
						token = reader.peek();
						dev.name = reader.nextString();
					}

					if ("privileges".equals(fieldname)) {
						dev.privileges = new ArrayList<>();
						reader.beginArray();
						while (reader.hasNext()) {
							dev.privileges.add(reader.nextString());
						}
						reader.endArray();
					}

				}
				reader.endObject();
				return dev;
			}

		}

		public static final class JokeAdapter extends TypeAdapter<Responses.Joke> {

			@Override
			public void write (JsonWriter out, Responses.Joke joke) throws IOException {
				out.jsonValue("[\"" + joke.joke + ", " + joke.punchline + "\"]");
			}

			@Override
			public Responses.Joke read (JsonReader reader) throws IOException {
				reader.beginArray();
				Responses.Joke joke = new Responses.Joke(reader.nextString(), reader.nextString());
				reader.endArray();
				return joke;
			}

		}

	}

}
