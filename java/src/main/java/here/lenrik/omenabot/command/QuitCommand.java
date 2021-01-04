package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import com.mojang.brigadier.CommandDispatcher;

import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;

public class QuitCommand {
	public static void register (CommandDispatcher<Object> dispatcher) {
		dispatcher.register(
				literal("quit").executes(ctx -> {
					((OmenaBot.BotCommandSource) ctx.getSource()).getBot().getUi().dispose();
					return 0;
				})
		);
	}

}
