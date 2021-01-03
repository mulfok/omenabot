package here.lenrik.omenabot;

import here.lenrik.omenabot.config.ConfigManager;
import here.lenrik.omenabot.ui.BotUI;

import javax.security.auth.login.LoginException;
import java.util.*;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.ParseResults;
import com.mojang.brigadier.builder.LiteralArgumentBuilder;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import com.mojang.brigadier.tree.CommandNode;
import net.dv8tion.jda.api.JDA;
import net.dv8tion.jda.api.JDABuilder;
import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.Message;
import net.dv8tion.jda.api.entities.MessageChannel;
import net.dv8tion.jda.api.events.Event;
import net.dv8tion.jda.api.events.GenericEvent;
import net.dv8tion.jda.api.events.ReadyEvent;
import net.dv8tion.jda.api.events.message.MessageReceivedEvent;
import net.dv8tion.jda.api.events.message.guild.GuildMessageReceivedEvent;
import net.dv8tion.jda.api.hooks.ListenerAdapter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jetbrains.annotations.NotNull;

import static com.mojang.brigadier.builder.LiteralArgumentBuilder.literal;

public class OmenaBot extends ListenerAdapter {
	public static Logger LOGGER = LogManager.getLogger("OmenaBot");
	public static CommandDispatcher<BotCommandSource> dispatcher = new CommandDispatcher<>();
	public ConfigManager config;
	private final BotUI ui;

	JDA discordApi;

	@SuppressWarnings("unchecked")
	public OmenaBot (ConfigManager config, BotUI ui) throws LoginException {
		this.config = config;
		this.ui = ui;
		dispatcher.register(
						(LiteralArgumentBuilder<BotCommandSource>) (Object) literal("ping").executes(context -> {
							long processing = new Date().getTime() - ((BotCommandSource) context.getSource()).createdTime;
							long ping = ((BotCommandSource) context.getSource()).getJDA().getGatewayPing();
							((BotCommandSource) context.getSource()).getEvent().getChannel().sendMessage("pong! (processing:" + processing + "ms, ping:" + ping + "ms)").queue();
							return 0;
						})
		);
		dispatcher.register(
						(LiteralArgumentBuilder<BotCommandSource>) (Object) literal("quit").executes(ctx -> {
							((BotCommandSource) ctx.getSource()).getBot().ui.dispose();
							return 0;
						})
		);
		discordApi = JDABuilder.createDefault(config.botSettings.token).addEventListeners(this).build();
	}

	@Override
	public void onGenericEvent (@NotNull GenericEvent event) {
		super.onGenericEvent(event);
		ui.updateStatus(event);
	}

	@Override
	public void onReady (@NotNull ReadyEvent event) {
		ui.updateStatus(event);
		for(Guild guild: event.getJDA().getGuilds()) {
			config.servers.get(guild.getId()).name = guild.getName();
		}
		LOGGER.info(config.servers);
	}


	@Override
	@SuppressWarnings({"unchecked", "OptionalGetWithoutIsPresent"})
	public void onGuildMessageReceived (@NotNull GuildMessageReceivedEvent event) {
		BotCommandSource source = new BotCommandSource(event, this);
		ConfigManager.ServerSettings settings = config.servers.get(event.getMessage().getGuild().getId());
		String prefix = settings.prefix;
		if (event.getMessage().getContentRaw().startsWith(prefix) && !event.getMessage().getContentRaw().startsWith(prefix.repeat(2))) {
			String messageContentsNoPrefix = event.getMessage().getContentRaw().replaceFirst(prefix.translateEscapes(), "");
			ParseResults<BotCommandSource> parse = dispatcher.parse(messageContentsNoPrefix, source);
			if (parse.getContext().getCommand() != null) {
				if (parse.getExceptions().isEmpty()) {
					try {
						dispatcher.execute(parse);
					} catch (CommandSyntaxException e) {
						LOGGER.fatal("There's a bug in com.mojang:brigadier; error:", e);
					}
				} else {
					Map<CommandNode<BotCommandSource>, CommandSyntaxException> e = parse.getExceptions();
					final boolean a[] = {false};
					e.forEach((key, eroor) -> a[0] |= eroor.getMessage().startsWith("Unknown command at position "));
					if (a[0]) {
						event.getChannel().sendMessage((e.values()).stream().unordered().findFirst().get().getMessage()).queue();
					}
				}
			}
		} else {
			HashMap<String, ConfigManager.ServerSettings.Id_s> channels = settings.channels;
			if (channels != null) {
				ConfigManager.ServerSettings.Id_s imageOnly = channels.get("image-only");
				if(imageOnly != null) {
					if (imageOnly.get() instanceof Long) {
						Long channel = (Long) imageOnly.get();
						if (channel.equals(event.getChannel().getIdLong()) && event.getMessage().getAttachments().size() < 1) {
							event.getMessage().delete().queue();
						}
					} else if (imageOnly.get() instanceof List) {
						for (Long channel : (ArrayList<Long>) imageOnly.get()) {
							if (channel.equals(event.getChannel().getIdLong()) && event.getMessage().getAttachments().size() < 1) {
								event.getMessage().delete().queue();
							}
						}
					}
				}
			}
		}
		LOGGER.debug(event.getMessage());
	}

	public void shutdown () {
		discordApi.shutdown();
	}

	public static class BotCommandSource {
		MessageEvent event;
		private OmenaBot bot;
		long createdTime = new Date().getTime();

		public BotCommandSource (MessageReceivedEvent event, OmenaBot omenaBot) {
			this.event = new MessageEvent(event);
			this.bot = omenaBot;
		}

		public BotCommandSource (GuildMessageReceivedEvent event, OmenaBot omenaBot) {
			this.event = new MessageEvent(event);
			this.bot = omenaBot;
		}

		public static class MessageEvent extends Event{

			private Message message;
			private MessageChannel channel;

			public MessageEvent (MessageReceivedEvent event){
				this(event.getJDA());
				message = event.getMessage();
				channel = event.getChannel();
			}

			public MessageEvent (GuildMessageReceivedEvent event){
				this(event.getJDA());
				channel = event.getChannel();
				message = event.getMessage();
			}

			public MessageEvent (@NotNull JDA api) {
				super(api);
			}

			public MessageChannel getChannel(){
				return channel;
			}

			public Message getMessage () {
				return message;
			}

		}

		public MessageEvent getEvent () {
			return event;
		}

		@SuppressWarnings("unused")
		public void setEvent (MessageReceivedEvent event) {
			this.event = new MessageEvent(event);
		}

		public OmenaBot getBot () {
			return bot;
		}

		@SuppressWarnings("unused")
		public void setBot (OmenaBot bot) {
			this.bot = bot;
		}

		public JDA getJDA () {
			return bot.discordApi;
		}

	}

}
