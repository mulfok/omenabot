package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.GuildChannel;
import net.dv8tion.jda.api.entities.Member;

import static com.mojang.brigadier.arguments.StringArgumentType.greedyString;
import static com.mojang.brigadier.arguments.StringArgumentType.string;
import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;
import static com.mojang.brigadier.builder.RequiredArgumentBuilder.argument;
import static here.lenrik.omenabot.command.MentionArgumentType.mention;

public class SetCommand {
	public static void register (CommandDispatcher<Object> dispatcher) {
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
													Guild guild = ((GuildChannel) ((OmenaBot.BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
													final OmenaBot bot = ((OmenaBot.BotCommandSource) context.getSource()).getBot();
													final Member member = MentionArgumentType.getMention(context, "user");
													final String nick = StringArgumentType.getString(context, "nick");
													bot.config.servers.get(guild.getId()).nicks.put(member.getId(), nick);
													bot.getUi().configTab.updatetConfig();
													bot.config.save();
													OmenaBot.LOGGER.debug("set nickname for guild: {}, user: {}, nick {}",
															guild.getName(),
															member.getUser().getName(),
															nick
													);
													return 0;
												}
										)
								).executes(
										(context) -> {
											Guild guild = ((GuildChannel) ((OmenaBot.BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
											final OmenaBot bot = ((OmenaBot.BotCommandSource) context.getSource()).getBot();
											final Member member = MentionArgumentType.getMention(context, "user");
											bot.config.servers.get(guild.getId()).nicks.remove(member.getId());
											bot.getUi().configTab.updatetConfig();
											bot.config.save();
											OmenaBot.LOGGER.info("unset nickname guild: {}, user: {}",
													guild.getName(),
													member.getUser().getName()
											);
											return 0;
										}
								)
						)
				)
		);
	}

}
