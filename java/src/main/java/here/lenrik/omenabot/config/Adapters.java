package here.lenrik.omenabot.config;

import java.io.IOException;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

import com.google.gson.GsonBuilder;
import com.google.gson.TypeAdapter;
import com.google.gson.stream.JsonReader;
import com.google.gson.stream.JsonToken;
import com.google.gson.stream.JsonWriter;

import static com.google.gson.stream.JsonToken.NAME;
import static here.lenrik.omenabot.config.ConfigManager.serversType;
import static here.lenrik.omenabot.config.Responses.Joke;

public class Adapters {

	public static void register (GsonBuilder builder) {
		builder.registerTypeAdapter(Responses.class, new Adapters.ResponsesA());
		builder.registerTypeAdapter(Responses.Joke.class, new Adapters.JokeA());
		builder.registerTypeAdapter(BotSettings.Dev.class, new Adapters.Dev());
		builder.registerTypeAdapter(BotSettings.class, new Adapters.BotSettingsA());
		builder.registerTypeAdapter(ServerSettings.class, new Adapters.ServerSettingsA());
		builder.registerTypeAdapter(serversType, new Adapters.Servers());
	}
/*
	public static final class Id_sA extends TypeAdapter<ServerSettings.Id_s>{

		public void write (JsonWriter out, ServerSettings.Id_s id_s) throws IOException {
			if(id_s == null){
				out.nullValue();
				return;
			}
			if(id_s.isList()){

			}else{
				out.value(id_s.getLong());
			}
		}

		public ServerSettings.Id_s read (JsonReader in) throws IOException {
			return null;
		}

	}*/

	public static final class ServerSettingsA extends TypeAdapter<ServerSettings> {

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
					if (id_s.isList()) {
						out.beginArray();
						for (Long id : id_s.getList()) {
							out.value(id);
						}
						out.endArray();
					} else {
						out.value((Long) id_s.get());
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
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(NAME)) {
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

	public static final class Servers extends TypeAdapter<HashMap<String, ServerSettings>> {

		@Override
		public void write (JsonWriter out, HashMap<String, ServerSettings> servers) throws IOException {
			if (servers == null) {
				out.nullValue();
				return;
			}
			out.setIndent("\t");
			out.beginObject();
			for (Map.Entry<String, ServerSettings> server : servers.entrySet()) {
				out.name(server.getKey());
				ConfigManager.gson.getAdapter(ServerSettings.class).write(out, server.getValue());
			}
			out.endObject();
		}

		@Override
		public HashMap<String, ServerSettings> read (JsonReader reader) throws IOException {
			var servers = new HashMap<String, ServerSettings>();
			reader.beginObject();
			while (reader.hasNext()) {
				reader.peek();
				servers.put(reader.nextName(), ConfigManager.gson.getAdapter(ServerSettings.class).read(reader));
			}
			reader.endObject();
			return servers;
		}

	}

	public static final class JokeA extends TypeAdapter<Joke> {

		@Override
		public void write (JsonWriter out, Joke joke) throws IOException {
			out.jsonValue("[\"" + joke.joke + "\", \"" + joke.punchline + "\"]");
		}

		@Override
		public Joke read (JsonReader reader) throws IOException {
			reader.beginArray();
			Joke joke = new Joke(reader.nextString(), reader.nextString());
			reader.endArray();
			return joke;
		}

	}

	public static final class Dev extends TypeAdapter<BotSettings.Dev> {

		@Override
		public void write (JsonWriter out, BotSettings.Dev dev) throws IOException {
			if (dev == null) {
				out.nullValue();
				return;
			}
			StringBuilder builder = new StringBuilder("{\"name\": \"");
			builder.append(dev.name.replaceAll("\"", "\\\\\\\"")).append('"');
			if (dev.privileges != null && dev.privileges.size() > 0) {
				builder.append(", \"privileges\": [\"").append(String.join("\", \"", dev.privileges)).append("\"]");
			}
			out.jsonValue(builder.append('}').toString());
		}

		@Override
		public BotSettings.Dev read (JsonReader reader) throws IOException {
			BotSettings.Dev dev = new BotSettings.Dev();
			reader.beginObject();
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(NAME)) {
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

	public static final class BotSettingsA extends TypeAdapter<BotSettings> {

		@Override
		public void write (JsonWriter out, BotSettings settings) throws IOException {
			if (settings == null) {
				out.nullValue();
				return;
			}
			out.beginObject();
			out.name("tokens");
			out.beginObject();
			for (var entry : settings.tokens.entrySet()) {
				out.name(entry.getKey());
				out.value(entry.getValue());
			}
			out.endObject();
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
		public BotSettings read (JsonReader reader) throws IOException {
			BotSettings settings = new BotSettings();
			reader.beginObject();
			String fieldName = null;

			while (reader.hasNext()) {
				JsonToken token = reader.peek();

				if (token.equals(NAME)) {
					//get the current token
					fieldName = reader.nextName();
				}

				if ("tokens".equals(fieldName)) {
					settings.tokens = new HashMap<>();
					reader.beginObject();
					while (reader.hasNext()) {
						settings.tokens.put(reader.nextName(), reader.nextString());
					}
					reader.endObject();
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
						settings.devs.put(reader.nextName(), ConfigManager.gson.getAdapter(BotSettings.Dev.class).read(reader));
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

	public static final class ResponsesA extends TypeAdapter<Responses> {

		@Override
		public void write (JsonWriter out, Responses responses) throws IOException {
			if (responses == null) {
				out.nullValue();
				return;
			}
			out.setIndent("\t");
			out.beginObject();
			out.name("trivia");
			{
				out.beginArray();
				for (String fact : responses.trivia) {
					out.value(fact);
				}
				out.endArray();
			}
			out.name("_8ball");
			{
				out.beginArray();
				for (String roll : responses._8ball) {
					out.value(roll);
				}
				out.endArray();
			}
			out.name("jokes");
			{
				out.beginArray();
				for (Joke joke : responses.jokes) {
					ConfigManager.gson.getAdapter(Joke.class).write(out, joke);
				}
				out.endArray();
			}
			out.name("hack");
			{
				out.beginObject();
				out.name("companies");
				{
					out.beginArray();
					for (String company : responses.hack.companies) {
						out.value(company);
					}
					out.endArray();
				}
				out.name("homework");
				{
					out.beginArray();
					for (String company : responses.hack.homework) {
						out.value(company);
					}
					out.endArray();
				}
				out.name("payment");
				{
					out.beginArray();
					for (String company : responses.hack.payment) {
						out.value(company);
					}
					out.endArray();
				}
				out.name("mail_provider");
				{
					out.beginArray();
					for (String company : responses.hack.mail_provider) {
						out.value(company);
					}
					out.endArray();
				}
				out.name("mail_body");
				{
					out.beginArray();
					for (ArrayList<String> company : responses.hack.mail_body) {
						out.jsonValue("[\"" + company.get(0) + "\", \"" + company.get(1) + "\"]");
					}
					out.endArray();
				}
				out.endObject();
			}
			out.name("anime");
			{
				out.beginArray();
				for (String link : responses.anime) {
					out.value(link);
				}
				out.endArray();
			}
			out.name("f");
			{
				out.beginArray();
				for (String link : responses.f) {
					out.value(link);
				}
				out.endArray();
			}
			out.name("mc_commands");
			{
				out.beginObject();
				for (Map.Entry<String, HashMap<String, String>> version : responses.mc_commands.entrySet()) {
					out.name(version.getKey());
					{
						out.beginObject();
						for (Map.Entry<String, String> command : version.getValue().entrySet()) {
							out.name(command.getKey());
							out.value(command.getValue());
						}
						out.endObject();
					}
				}
				out.endObject();
			}
			out.name("pong_loss");
			{
				out.beginArray();
				for (String line : responses.pong_loss) {
					out.value(line);
				}
				out.endArray();
			}
			out.name("pong_win");
			{
				out.beginArray();
				for (String link : responses.pong_win) {
					out.value(link);
				}
				out.endArray();
			}
			out.endObject();
		}

		@Override
		public Responses read (JsonReader reader) throws IOException {
			Responses responses = new Responses();
			reader.beginObject();
			String fieldName = null;
			while (reader.hasNext()) {
				if (reader.peek() == NAME) {
					fieldName = reader.nextName();
				} else {
					assert fieldName != null;
					if (fieldName.equals("mc_commands") || fieldName.equals("hack")) {
						reader.beginObject();
					} else {
						reader.beginArray();
					}
					switch (fieldName) {
						case "trivia" -> {
							while (reader.hasNext())
								responses.trivia.add(reader.nextString());
						}
						case "_8ball" -> {
							while (reader.hasNext())
								responses._8ball.add(reader.nextString());
						}
						case "jokes" -> {
							while (reader.hasNext())
								responses.jokes.add(ConfigManager.gson.getAdapter(Joke.class).read(reader));
						}
						case "hack" -> {
							String step = null;
							while (reader.hasNext()) {
								if (reader.peek() == NAME) {
									step = reader.nextName();
								} else {
									assert step != null;
									reader.beginArray();
									if (step.equals("mail_body")) {
										while (reader.hasNext()) {
											reader.beginArray();
											ArrayList<String> body = new ArrayList<>();
											body.add(reader.nextString());
											body.add(reader.nextString());
											responses.hack.mail_body.add(body);
											reader.endArray();
										}
									} else {
										ArrayList<String> stepList;
										switch (step) {
											case "payment" -> stepList = responses.hack.payment;
											case "homework" -> stepList = responses.hack.homework;
											case "companies" -> stepList = responses.hack.companies;
											case "mail_provider" -> stepList = responses.hack.mail_provider;
											default -> throw new IllegalStateException("Unexpected value: " + step);
										}
										while (reader.hasNext()) {
											stepList.add(reader.nextString());
										}
									}
									reader.endArray();
								}
							}
						}
						case "anime" -> {
							while (reader.hasNext())
								responses.anime.add(reader.nextString());
						}
						case "f" -> {
							while (reader.hasNext())
								responses.f.add(reader.nextString());
						}
						case "mc_commands" -> {
							while (reader.hasNext()) {
								AbstractMap.SimpleEntry<String, HashMap<String, String>> version = new AbstractMap.SimpleEntry<>(reader.nextName(), new HashMap<>());
								reader.beginObject();
								while (reader.hasNext()) {
									version.getValue().put(reader.nextName(), reader.nextString());
								}
								responses.mc_commands.put(version.getKey(), version.getValue());
								reader.endObject();
							}
						}
						case "pong_loss" -> {
							while (reader.hasNext())
								responses.pong_loss.add(reader.nextString());
						}
						case "pong_win" -> {
							while (reader.hasNext())
								responses.pong_win.add(reader.nextString());
						}
					}
					if (fieldName.equals("mc_commands") || fieldName.equals("hack")) {
						reader.endObject();
					} else {
						reader.endArray();
					}
				}
			}
			reader.endObject();
			return responses;
		}

	}

}
