package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import java.util.ArrayList;
import java.util.Collection;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import com.google.common.collect.Lists;
import com.mojang.brigadier.StringReader;
import com.mojang.brigadier.arguments.ArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.Dynamic2CommandExceptionType;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.GuildChannel;
import net.dv8tion.jda.api.entities.MessageChannel;

public class MessageChannelArgumentType implements ArgumentType<MessageChannel> {
	private static final Pattern pattern = Pattern.compile("<#?!?(\\d+)>");
	private static final Dynamic2CommandExceptionType NOT_A_MESSAGE_CHANNEL = new Dynamic2CommandExceptionType((channelName, type) -> "channel %s is not a message channel but a %s instead"::formatted);

	public static MessageChannelArgumentType channel () {
		return new MessageChannelArgumentType();
	}

	public static GuildChannel getChannel (CommandContext<Object> context, String channel) {
		return context.getArgument(channel, GuildChannel.class);
	}

	@Override
	public <S> MessageChannel parse (StringReader reader, S source) throws CommandSyntaxException {
		if (!reader.canRead()) {
			reader.skip();
		}
		int start = reader.getCursor();
		while (reader.canRead() && reader.peek() != ' ') {
			reader.skip();
		}
		String channelName = reader.getRead().substring(start, reader.getCursor() /*+ (reader.canRead()? 1 : 0)*/);
		Matcher matcher;
		OmenaBot.BotCommandSource commandSource = ((OmenaBot.BotCommandSource) source);
		final Guild guild = ((GuildChannel) commandSource.getEvent().getChannel()).getGuild();
		if ((matcher = pattern.matcher(channelName)).find()) {
			try {
				return (MessageChannel) guild.getGuildChannelById(Long.parseLong(matcher.group(1)));
			} catch (ClassCastException e) {
				throw CommandManager.INVALID_CONTEXT.create("channel mention", commandSource.getEvent().getChannel().getType());
			}
		} else {
			try {
				return Objects.requireNonNull((MessageChannel) guild.getGuildChannelById(channelName));
			} catch (ClassCastException cce) {
				throw NOT_A_MESSAGE_CHANNEL.create(guild.getGuildChannelById(channelName).getName(), guild.getGuildChannelById(channelName).getType().name());
			} catch (Exception e) {
				ArrayList<MessageChannel> matchingChannels = ((GuildChannel) commandSource.getEvent().getChannel()).getParent().getTextChannels().stream().filter((channel) -> channel.getName().matches(channelName)).collect(Collectors.toCollection(Lists::newArrayList));
				matchingChannels.addAll(guild.getTextChannelsByName(channelName, false));
				matchingChannels.addAll(guild.getTextChannelsByName(channelName, true));
				return matchingChannels.size() > 0 ? matchingChannels.get(0) : null;
			}
		}
	}

	@Override
	public <S> CompletableFuture<Suggestions> listSuggestions (CommandContext<S> context, SuggestionsBuilder builder) {
		return null;
	}

	@Override
	public Collection<String> getExamples () {
		return null;
	}

}
