package here.lenrik.omenabot.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.function.Consumer;
import java.util.function.Predicate;
import java.util.function.UnaryOperator;
import java.util.stream.Stream;

import com.google.common.collect.Sets;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.internal.LinkedTreeMap;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class ConfigManager {
	public static final GsonBuilder gBuilder;
	public static final Gson gson;

	public HashMap<String, ServerSettings> servers = new HashMap<>();
	public BotSettings botSettings = new BotSettings();
	public Responses responses = new Responses();

	static {
		gBuilder = new GsonBuilder();
		gson = new Gson();
	}

	public void load (String location) {
		try {
			botSettings = BotSettings.load(location + "/private/bot.json");
			responses = Responses.load(location + "/responselists.json");
			servers = gson.fromJson(Files.readString(Path.of(location + "/private/servers.json")), HashMap.class);
		} catch (IOException e) {
			e.printStackTrace();
		}
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

		}

	}

	public static class ServerSettings extends AbstractMap<String, Object> {
		@Nullable
		@SuppressWarnings("unused")
		public String name;
		@NotNull
		public String prefix = "~";
		@SuppressWarnings("unused")
		public LinkedTreeMap<String, String> nicks;
		@SuppressWarnings("unused")
		public LinkedTreeMap<String, ?> channels;

		public static ServerSettings fromMap (LinkedTreeMap serverSettings) {
			ServerSettings settings = new ServerSettings();
			settings.name = (String) serverSettings.get("name");
			settings.nicks = (LinkedTreeMap<String, String>) serverSettings.get("nicks");
			settings.prefix = (String) serverSettings.get("prefix");
			settings.channels = (LinkedTreeMap<String, ?>) serverSettings.get("channels");
			return settings;
		}

		@NotNull
		@Override
		public Set<Entry<String, Object>> entrySet () {
			Set<Entry<String, Object>> set = Sets.newIdentityHashSet();
			set.add(new SimpleEntry<>("prefix", prefix));
			if (name != null) {
				set.add(new SimpleEntry<>("name", name));
			}
			if (nicks != null) {
				set.add(new SimpleEntry<>("nicks", nicks));
			}
			if (channels != null) {
				set.add(new SimpleEntry<>("channels", channels));
			}
			return set;
		}

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

		public static class Joke implements List<String> {

			public String joke = "";
			public String punchline = "";

			@Override
			public int size () {
				return joke.isEmpty() || punchline.isEmpty() ? 0 : 2;
			}

			@Override
			public boolean isEmpty () {
				return joke.isEmpty() || punchline.isEmpty();
			}

			@Override
			public boolean contains (Object o) {
				return joke.equals(o) || punchline.equals(o);
			}

			@NotNull
			@Override
			public Iterator<String> iterator () {
				List<String> list = new ArrayList<>(Collections.singletonList(joke));
				list.add(punchline);
				return list.iterator();
			}

			@Override
			public void forEach (Consumer<? super String> action) {
				action.accept(joke);
				action.accept(punchline);
			}

			@NotNull
			@Override
			public Object[] toArray () {
				return new Object[]{joke, punchline};
			}

			@Override
			public boolean add (String o) {
				if (joke.isEmpty()) {
					joke = o;
				} else if (punchline.isEmpty()) {
					punchline = o;
				} else {
					throw new RuntimeException("Cannot add values to a joke");
				}
				return true;
			}

			@Override
			public boolean remove (Object o) {
				throw new RuntimeException("Cannot remove values from a joke");
			}

			@Override
			public boolean addAll (@NotNull Collection collection) {
				throw new RuntimeException("Cannot add values to a joke");
			}

			@Override
			public boolean removeIf (Predicate filter) {
				throw new RuntimeException("Cannot remove values from a joke");
			}

			@Override
			public boolean addAll (int i, @NotNull Collection collection) {
				throw new RuntimeException("Cannot add values to a joke");
			}

			@Override
			public void replaceAll (UnaryOperator operator) {

			}

			@Override
			public void sort (Comparator c) {

			}

			@Override
			public void clear () {

			}

			@Override
			public String get (int i) {
				return null;
			}

			@Override
			public String set (int i, String o) {
				return null;
			}

			@Override
			public void add (int i, String o) {

			}

			@Override
			public String remove (int i) {
				return null;
			}

			@Override
			public int indexOf (Object o) {
				return 0;
			}

			@Override
			public int lastIndexOf (Object o) {
				return 0;
			}

			@NotNull
			@Override
			public ListIterator<String> listIterator () {
				return (ListIterator<String>) this.iterator();
			}

			@NotNull
			@Override
			public ListIterator<String> listIterator (int i) {
				return null;
			}

			@NotNull
			@Override
			public List<String> subList (int i, int i1) {
				return null;
			}

			@Override
			public Spliterator<String> spliterator () {
				return null;
			}

			@Override
			public Stream<String> stream () {
				return null;
			}

			@Override
			public Stream<String> parallelStream () {
				return null;
			}

			@Override
			public boolean retainAll (@NotNull Collection collection) {
				return false;
			}

			@Override
			public boolean removeAll (@NotNull Collection collection) {
				return false;
			}

			@Override
			public boolean containsAll (@NotNull Collection collection) {
				return false;
			}

			@NotNull
			@Override
			public Object[] toArray (@NotNull Object[] objects) {
				return new Object[0];
			}

		}

		public static Responses load (String location) throws IOException {
			String json = Files.readString(Path.of(location));
			return ConfigManager.gson.fromJson(json, Responses.class);
		}

	}


}
