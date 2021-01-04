package here.lenrik.omenabot.command;

import com.mojang.brigadier.CommandDispatcher;

public class CommandManager {
	public static void register (CommandDispatcher<Object> dispatcher) {
		PingCommand.register(dispatcher);
		QuitCommand.register(dispatcher);
		SetCommand.register(dispatcher);
	}


}
