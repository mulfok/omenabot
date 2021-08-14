package here.lenrik.omenabot.command;

import com.mojang.brigadier.CommandDispatcher;

import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;
import static com.mojang.brigadier.builder.RequiredArgumentBuilder.argument;
import static here.lenrik.omenabot.command.MentionArgumentType.mention;

public class HackCommand {
	public static void register (CommandDispatcher<Object> dispatcher) {
		dispatcher.register(
				literal(
						"hack"
				).then(
						argument(
								"user",
								mention()
						).executes(
								context -> {
									 return 0;
								}
						)
				)
		);
	}

}
