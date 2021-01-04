package here.lenrik.omenabot.command;

import here.lenrik.omenabot.OmenaBot;

import java.util.Date;

import com.mojang.brigadier.CommandDispatcher;

import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;

public class PingCommand {
	public static void register (CommandDispatcher<Object> dispatcher) {
		dispatcher.register(
				literal(
						"ping"
				).executes(
						context -> {
							long processing = new Date().getTime() - ((OmenaBot.BotCommandSource) context.getSource()).getCreatedTime();
							long ping = ((OmenaBot.BotCommandSource) context.getSource()).getJDA().getGatewayPing();
							((OmenaBot.BotCommandSource) context.getSource()).getEvent().getChannel().sendMessage("pong! (processing:" + processing + "ms, ping:" + ping + "ms)").queue();
							return 0;
						}

				)
		);
	}
}
