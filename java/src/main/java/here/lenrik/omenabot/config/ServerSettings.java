package here.lenrik.omenabot.config;

import java.util.ArrayList;
import java.util.HashMap;

import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public class ServerSettings {
	@NotNull
	@SuppressWarnings("unused")
	public String name = "";
	@NotNull
	public String prefix = "~";
	@SuppressWarnings("unused")
	public HashMap<String, String> nicks;
	@SuppressWarnings("unused")
	public HashMap<String, Id_s> channels;

	public ServerSettings () {}

	public static class Id_s {
		@NotNull
		final Long id;
		@Nullable
		final ArrayList<Long> ids;

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
