package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import com.mojang.brigadier.CommandDispatcher;

import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;
import static com.mojang.brigadier.builder.RequiredArgumentBuilder.argument;

public class TestCommand {
	public static void register (CommandDispatcher<Object> dispatcher) {
		dispatcher.register(
				literal(
						"test"
				).then(
						literal(
								"member"
						).then(
								argument(
										"mention",
										MentionArgumentType.mention()
								).executes(
										(s) -> {
											OmenaBot.LOGGER.info(
													MentionArgumentType.getMention(
															s,
															"mention"
													)
											);
											return 0;
										}
								)
						)
				)
		);
	}

}
