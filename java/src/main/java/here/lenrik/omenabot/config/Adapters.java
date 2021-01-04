package here.lenrik.omenabot.config;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;

public class Adapters {
	public static final class ServerSettings extends TypeAdapter<here.lenrik.omenabot.config.ServerSettings> {

		@Override
		public void write (JsonWriter out, here.lenrik.omenabot.config.ServerSettings settings) throws IOException {
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
					here.lenrik.omenabot.config.ServerSettings.Id_s id_s = channel.getValue();
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
		public here.lenrik.omenabot.config.ServerSettings read (JsonReader reader) throws IOException {
			here.lenrik.omenabot.config.ServerSettings settings = new here.lenrik.omenabot.config.ServerSettings();
			reader.beginObject();
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(JsonToken.NAME)) {
					//get the current token
					fieldName = reader.nextName();
				}

				if ("name".equals(fieldName)) {
					//move to next token
					reader.peek();
					settings.name = reader.nextString();
				}

				if ("prefix".equals(fieldName)) {
					//move to next token
					reader.peek();
					settings.prefix = reader.nextString();
				}

				if ("nicks".equals(fieldName)) {
					settings.nicks = new HashMap<>();
					reader.beginObject();
					while (reader.hasNext()) {
						settings.nicks.put(reader.nextName(), reader.nextString());
					}
					reader.endObject();
				}

				if ("channels".equals(fieldName)) {
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
							settings.channels.put(channel, here.lenrik.omenabot.config.ServerSettings.Id_s.valueOf(ids));
						} else {
							settings.channels.put(channel, here.lenrik.omenabot.config.ServerSettings.Id_s.valueOf(reader.nextLong()));
						}
					}
					reader.endObject();
				}
			}
			reader.endObject();
			return settings;
		}

	}

	public static final class Servers extends TypeAdapter<HashMap<String, here.lenrik.omenabot.config.ServerSettings>> {

		@Override
		public void write (JsonWriter out, HashMap<String, here.lenrik.omenabot.config.ServerSettings> servers) throws IOException {
			if (servers == null) {
				out.nullValue();
				return;
			}
			out.setIndent("\t");
			out.beginObject();
			for (Map.Entry<String, here.lenrik.omenabot.config.ServerSettings> server : servers.entrySet()) {
				out.name(server.getKey());
				ConfigManager.gson.getAdapter(here.lenrik.omenabot.config.ServerSettings.class).write(out, server.getValue());
			}
			out.endObject();
		}

		@Override
		public HashMap<String, here.lenrik.omenabot.config.ServerSettings> read (JsonReader reader) throws IOException {
			var servers = new HashMap<String, here.lenrik.omenabot.config.ServerSettings>();
			reader.beginObject();
			while (reader.hasNext()) {
				reader.peek();
				servers.put(reader.nextName(), ConfigManager.gson.getAdapter(here.lenrik.omenabot.config.ServerSettings.class).read(reader));
			}
			reader.endObject();
			return servers;
		}

	}

	public static final class Joke extends TypeAdapter<Responses.Joke> {

		@Override
		public void write (JsonWriter out, Responses.Joke joke) throws IOException {
			out.jsonValue("[\"" + joke.joke + "\", \"" + joke.punchline + "\"]");
		}

		@Override
		public Responses.Joke read (JsonReader reader) throws IOException {
			reader.beginArray();
			Responses.Joke joke = new Responses.Joke(reader.nextString(), reader.nextString());
			reader.endArray();
			return joke;
		}

	}

	public static final class Dev extends TypeAdapter<here.lenrik.omenabot.config.BotSettings.Dev> {

		@Override
		public void write (JsonWriter out, here.lenrik.omenabot.config.BotSettings.Dev dev) throws IOException {
			if (dev == null) {
				out.nullValue();
				return;
			}
			StringBuilder builder = new StringBuilder("{\"name\": \"");
			builder.append(dev.name).append('"');
			if (dev.privileges != null && dev.privileges.size() > 0) {
				builder.append(", [\"").append(String.join("\", \"", dev.privileges)).append("\"]");
			}
			out.jsonValue(builder.append('}').toString());
		}

		@Override
		public here.lenrik.omenabot.config.BotSettings.Dev read (JsonReader reader) throws IOException {
			here.lenrik.omenabot.config.BotSettings.Dev dev = new here.lenrik.omenabot.config.BotSettings.Dev();
			reader.beginObject();
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(JsonToken.NAME)) {
					//get the current token
					fieldName = reader.nextName();
				}

				if ("name".equals(fieldName)) {
					//move to next token
					reader.peek();
					dev.name = reader.nextString();
				}

				if ("privileges".equals(fieldName)) {
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

	public static final class BotSettings extends TypeAdapter<here.lenrik.omenabot.config.BotSettings> {

		@Override
		public void write (JsonWriter out, here.lenrik.omenabot.config.BotSettings settings) throws IOException {
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
					out.jsonValue(ConfigManager.gson.toJson(dev.getValue()));
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
		public here.lenrik.omenabot.config.BotSettings read (JsonReader reader) throws IOException {
			here.lenrik.omenabot.config.BotSettings settings = new here.lenrik.omenabot.config.BotSettings();
			reader.beginObject();
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(JsonToken.NAME)) {
					//get the current token
					fieldName = reader.nextName();
				}

				if ("token".equals(fieldName)) {
					//move to next token
					reader.peek();
					settings.token = reader.nextString();
				}

				if ("devs".equals(fieldName)) {
					settings.devs = new HashMap<>();
					reader.beginObject();
					while (reader.hasNext()) {
						settings.devs.put(reader.nextName(), ConfigManager.gson.getAdapter(here.lenrik.omenabot.config.BotSettings.Dev.class).read(reader));
					}
					reader.endObject();
				}

				if ("ping".equals(fieldName)) {
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

}
