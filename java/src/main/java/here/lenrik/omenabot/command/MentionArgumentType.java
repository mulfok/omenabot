package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import java.util.Collection;
import java.util.concurrent.CompletableFuture;

import com.mojang.brigadier.StringReader;
import com.mojang.brigadier.arguments.ArgumentType;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.exceptions.DynamicCommandExceptionType;
import com.mojang.brigadier.suggestion.Suggestions;
import com.mojang.brigadier.suggestion.SuggestionsBuilder;
import net.dv8tion.jda.api.entities.Member;

public class MentionArgumentType implements ArgumentType<Member> {
	private final static DynamicCommandExceptionType AMBIGIOUS_NAME = new DynamicCommandExceptionType((name) -> "Ambigious name %s"::formatted);

	public static MentionArgumentType mention () {
		return new MentionArgumentType();
	}

	public static Member getMention (CommandContext<Object> context, String user) {
		return null;
	}

	@Override
	public Member parse (StringReader reader) throws CommandSyntaxException {
//		OmenaBot.INSTANCE.getApi().;
		return null;
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
