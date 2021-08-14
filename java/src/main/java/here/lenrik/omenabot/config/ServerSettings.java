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
		@NotNull final ArrayList<Long> ids = new ArrayList<>();

		public Id_s (@Nullable ArrayList<Long> ids) {
			this.ids.addAll(ids);
		}

		public Id_s (Long id) {
			this.ids.add(id);
		}

		public Id_s () {

		}

		public static Id_s valueOf (ArrayList<Long> ids) {
			return new Id_s(ids);
		}

		public Object get () {
			return ids.size() == 1 ? ids.get(0) : ids;
		}

		public Long get (int index) {
			return ids.get(index);
		}

		public Long getLong(){
			return get(0);
		}

		public ArrayList<Long> getList(){
			return ids;
		}

		public static Id_s valueOf (Long value) {
			return new Id_s(value);
		}

		public boolean isList(){
			return ids.size() > 1;
		}

		public boolean add(Long id){
			if(ids.contains(id)){
				return false;
			}
			ids.add(id);
			return true;
		}

		public boolean remove(Long id){
			return ids.remove(id);
		}
		public boolean contaions(Long id){
			return ids.contains(id);
		}

		@Override
		public String toString () {
			return ids.size() == 1 ? ids.get(0).toString() : ids.toString();
		}

		public boolean isEmpty () {
			return ids.isEmpty();
		}

	}

	@Override
	public String toString () {
		return name + "{prefix='" + prefix + "'" + (nicks != null ? ", nicks:" + nicks : "") + (channels != null ? ", channels:" + channels : "") + "}";
	}

}
