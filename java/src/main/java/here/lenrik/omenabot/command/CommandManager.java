package here.lenrik.omenabot.command;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.exceptions.Dynamic2CommandExceptionType;

public class CommandManager {
	public static final Dynamic2CommandExceptionType INVALID_CONTEXT = new Dynamic2CommandExceptionType((command, context) -> "Cannot use %s in %s"::formatted);

	public static void register (CommandDispatcher<Object> dispatcher) {
		TestCommand.register(dispatcher);
		PingCommand.register(dispatcher);
		QuitCommand.register(dispatcher);
		SetCommand.register(dispatcher);
	}

}
