package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import java.util.Collection;
import java.util.concurrent.CompletableFuture;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import com.mojang.brigadier.StringReader;
import com.mojang.brigadier.arguments.ArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.DynamicCommandExceptionType;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.GuildChannel;
import net.dv8tion.jda.api.entities.Member;
import net.dv8tion.jda.api.entities.User;
import org.jetbrains.annotations.NotNull;

public class MentionArgumentType implements ArgumentType<Member> {
	private static final DynamicCommandExceptionType AMBIGUOUS_NAME = new DynamicCommandExceptionType((name) -> "Ambigious name %s"::formatted);// todo: probably also unnecessary
	private static final DynamicCommandExceptionType NOT_A_MEMBER = new DynamicCommandExceptionType((name)-> "User %s is not a member of this server"::formatted);
	private static final DynamicCommandExceptionType NOT_A_NAME = new DynamicCommandExceptionType((name) -> "Not a name %s (consider using a ping or user's id)."::formatted);
	private static final DynamicCommandExceptionType NO_SUCH_USER = new DynamicCommandExceptionType((name) -> "There's no user vith id %s"::formatted);
	private static final Pattern pattern = Pattern.compile("<@!?(\\d+)>");

	public static MentionArgumentType mention () {
		return new MentionArgumentType();
	}

	public static Member getMention (CommandContext<Object> context, String user) {
		return context.getArgument(user, Member.class);
	}

	@Override
	public <S> Member parse(StringReader reader, S source) throws CommandSyntaxException {
		if(!reader.canRead()){
			reader.skip();
		}
		if (source instanceof OmenaBot.BotCommandSource) {
			int start = reader.getCursor(), end;
			boolean possibleIdTag = reader.peek() == '<';
			boolean possibleIdInt = reader.peek() >= '0' && reader.peek() <= '9';
			boolean possibleAtTag = reader.peek() == '@';
			OmenaBot.BotCommandSource commandSource = (OmenaBot.BotCommandSource) source;
			if(!(possibleAtTag || possibleIdInt || possibleIdTag)){
				throw NOT_A_NAME.create(reader.readString());
			}
			if(!(commandSource.getEvent().getChannel() instanceof GuildChannel)){
				throw CommandManager.INVALID_CONTEXT.create("\"usenick\"", commandSource.getEvent().getChannel().getType().name());
			}
			Guild guild = ((GuildChannel)commandSource.getEvent().getChannel()).getGuild();
			if (possibleIdTag) {
				while (reader.peek() != '>' || Character.isWhitespace(reader.peek())) {
					reader.skip();
				}
				if (reader.peek() == '>'){
					reader.skip();
				}
				end = reader.getCursor();
				String mention = reader.getString().substring(start, end);
				Matcher matcher = pattern.matcher(mention);
				OmenaBot.LOGGER.info("text: {}, mention(?): {}", mention, matcher.find());
				if(matcher.matches()){
					final String id = matcher.group(1);
					return getMember(guild, id);
				}
			} else if (possibleIdInt){
				return getMember(guild, Long.toString(reader.readLong()));
			}
			if(possibleAtTag){
				// TODO: check if that actually can happen?
			}
			OmenaBot.LOGGER.info(commandSource.getEvent());
		} else {
			OmenaBot.LOGGER.info("Not BotCommandSource passed into parse");
		}
		return null;
	}

	@NotNull
	private static Member getMember (Guild guild, String id) throws CommandSyntaxException {
		Member member = guild.getMemberById(id);
		if (member == null) {
			member = guild.retrieveMemberById(id).complete();
		}
		if (member != null) {
			return member;
		}
		User user = guild.getJDA().getUserById(id);
		if (user == null) {
			user = guild.getJDA().retrieveUserById(id).complete();
		}
		if (user != null) {
			throw NOT_A_MEMBER.create(user.getName());
		}
		else throw NO_SUCH_USER.create(id);
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
