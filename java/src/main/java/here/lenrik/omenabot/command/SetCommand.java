package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;

import static com.mojang.brigadier.arguments.StringArgumentType.greedyString;
import static com.mojang.brigadier.arguments.StringArgumentType.string;
import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;
import static com.mojang.brigadier.builder.RequiredArgumentBuilder.argument;
import static here.lenrik.omenabot.command.MentionArgumentType.mention;

public class SetCommand {
	public static void register ( CommandDispatcher<Object> dispatcher) {
		dispatcher.register(
				literal(
						"set"
				).then(
						literal(
								"channel"
						).then(
								argument(
										"name",
										string()
								)
						)
				).then(
						literal(
								"usernick"
						).then(
								argument(
										"user",
										mention()
								).then(
										argument(
												"nick",
												greedyString()
										).executes(
												(context) -> {
													OmenaBot.LOGGER.info("user: {}, nick {}",
															MentionArgumentType.getMention(context, "user").getUser().getName(),
															StringArgumentType.getString(context, "nick")
													);
													return 0;
												}
										)
								).executes(
										(context) -> {
											OmenaBot.LOGGER.info("user: {}", StringArgumentType.getString(context, "user"));
											return 0;
										}
								)
						)
				)
		);
	}

}
