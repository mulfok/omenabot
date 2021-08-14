package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;
import here.lenrik.omenabot.OmenaBot.BotCommandSource;
import here.lenrik.omenabot.config.ServerSettings;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.arguments.StringArgumentType;
import com.mojang.brigadier.context.CommandContext;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.GuildChannel;
import net.dv8tion.jda.api.entities.Member;
import org.apache.logging.log4j.LogManager;

import static com.mojang.brigadier.arguments.StringArgumentType.greedyString;
import static com.mojang.brigadier.arguments.StringArgumentType.string;
import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;
import static com.mojang.brigadier.builder.RequiredArgumentBuilder.argument;
import static here.lenrik.omenabot.command.MessageChannelArgumentType.channel;
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
								).then(
										literal(
												"here"
										).executes(
												SetCommand::toggleHere
										).then(
												literal(
														"add"
												).executes(
														SetCommand::addHere
												)
										).then(
												literal(
														"remove"
												).executes(
														SetCommand::removeHere
												)
										)
								).then(
										argument(
												"channel",
												channel()
										).executes(
												SetCommand::toggleExact
										).then(
												literal(
														"add"
												).executes(
														SetCommand::addExact
												)
										).then(
												literal(
														"remove"
												).executes(
														SetCommand::removeExact
												)
										)
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
													Guild guild = ((GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
													final OmenaBot bot = ((BotCommandSource) context.getSource()).getBot();
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
											Guild guild = ((GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
											final OmenaBot bot = ((BotCommandSource) context.getSource()).getBot();
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

	private static int toggleExact (CommandContext<Object> context) {
		final GuildChannel channel = MessageChannelArgumentType.getChannel(context, "channel");
		return toggleChannel(context, channel);
	}

	private static int toggleHere (CommandContext<Object> context) {
		final GuildChannel channel = (GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel();
		return toggleChannel(context, channel);
	}

	private static int toggleChannel (CommandContext<Object> context, GuildChannel channel) {
		final Guild guild = ((GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
		final ServerSettings settings = ((BotCommandSource) context.getSource()).getBot().config.servers.get(guild.getId());
		final String name = StringArgumentType.getString(context, "name");
		LogManager.getLogger(guild.getName()).debug("t: {}, {}", name, channel);
		return toggleChannelInList(settings, name, channel);
	}

	private static int toggleChannelInList (ServerSettings settings, String listName, GuildChannel channel) {
		if (settings.channels.getOrDefault(listName, new ServerSettings.Id_s()).contaions(channel.getIdLong())) {
			return removeChannelFromList(settings, listName, channel);
		} else {
			return addChannelToList(settings, listName, channel);
		}
	}

	private static int addExact (CommandContext<Object> context) {
		final GuildChannel channel = MessageChannelArgumentType.getChannel(context, "channel");
		return addChannel(context, channel);
	}

	private static int addHere (CommandContext<Object> context) {
		final GuildChannel channel = (GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel();
		return addChannel(context, channel);
	}

	private static int addChannel (CommandContext<Object> context, GuildChannel channel) {
		final Guild guild = ((GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel()).getGuild();
		final ServerSettings settings = ((BotCommandSource) context.getSource()).getBot().config.servers.get(guild.getId());
		final String name = StringArgumentType.getString(context, "name");
		LogManager.getLogger(guild.getName()).debug("a: {}, {}", name, channel);
		return addChannelToList(settings, name, channel);
	}

	private static int addChannelToList (ServerSettings settings, String listName, GuildChannel channel) {
		final ServerSettings.Id_s id_s = settings.channels.getOrDefault(listName, new ServerSettings.Id_s());
		id_s.add(channel.getIdLong());
		settings.channels.put(listName, id_s);
		return 0;
	}

	private static int removeExact (CommandContext<Object> context) {
		final GuildChannel channel = MessageChannelArgumentType.getChannel(context, "channel");
		return removeChannel(context, channel);
	}

	private static int removeHere (CommandContext<Object> context) {
		final GuildChannel channel = (GuildChannel) ((BotCommandSource) context.getSource()).getEvent().getChannel();
		return removeChannel(context, channel);
	}

	private static int removeChannel (CommandContext<Object> context, GuildChannel channel){
		final BotCommandSource source = (BotCommandSource) context.getSource();
		final Guild guild = ((GuildChannel) source.getEvent().getChannel()).getGuild();
		final ServerSettings settings = source.getBot().config.servers.get(guild.getId());
		final String name = StringArgumentType.getString(context, "name");
		LogManager.getLogger(guild.getName()).debug("r: {}, {}", name, channel);
		return removeChannelFromList(settings, name, channel);
	}

	private static int removeChannelFromList (ServerSettings settings, String listName, GuildChannel channel) {
		ServerSettings.Id_s r = settings.channels.get(listName);
		if (r != null) {
			final boolean remove = r.remove(channel.getIdLong());
			if (r.isEmpty()) {
				settings.channels.remove(listName);
			}
			return remove ? 1 : 0;
		}
		return 0;
	}

}
