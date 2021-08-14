package here.lenrik.omenabot;

import here.lenrik.omenabot.command.CommandManager;
import here.lenrik.omenabot.config.ConfigManager;
import here.lenrik.omenabot.config.ServerSettings;
import here.lenrik.omenabot.ui.BotUI;

import javax.security.auth.login.LoginException;
import java.util.*;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.RunnableFuture;
import java.util.regex.Pattern;

import com.mojang.brigadier.CommandDispatcher;
import com.mojang.brigadier.ParseResults;
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
import net.dv8tion.jda.api.requests.GatewayIntent;
import net.dv8tion.jda.api.utils.MemberCachePolicy;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.jetbrains.annotations.NotNull;

public class OmenaBot extends ListenerAdapter {
	public static final Logger LOGGER = LogManager.getLogger("OmenaBot");
	public static final ConcurrentLinkedQueue<RunnableFuture> mainThreadQueue = new ConcurrentLinkedQueue<>();
	public static final CommandDispatcher<Object> dispatcher = new CommandDispatcher<>();
	public static OmenaBot INSTANCE;
	public final ConfigManager config;
	private final BotUI ui;
	JDA discordApi;

	public OmenaBot (ConfigManager config, BotUI ui, String tokenName) throws LoginException {
		INSTANCE = this;
		this.config = config;
		this.ui = ui;
		CommandManager.register(dispatcher);
		discordApi =
				JDABuilder.createDefault(config.botSettings.tokens.get(tokenName)).enableIntents(GatewayIntent.GUILD_MEMBERS).addEventListeners(this).setMemberCachePolicy(MemberCachePolicy.ALL).build();
	}

	@Override
	public void onGenericEvent (@NotNull GenericEvent event) {
		super.onGenericEvent(event);
	}

	@Override
	public void onReady (@NotNull ReadyEvent event) {
		LogManager.getLogger("main").info("Hello it's {}", discordApi.getSelfUser().getName());
		ui.updateStatus(event);
		for (Guild guild : event.getJDA().getGuilds()) {
			config.servers.get(guild.getId()).name = guild.getName();
		}
		ArrayList<String> removalQueue = new ArrayList<>();
		for (Map.Entry<String, ServerSettings> settingsEntry : config.servers.entrySet()) {
			if (settingsEntry.getValue().name.isEmpty()) {
				removalQueue.add(settingsEntry.getKey());
			}
		}
		for (String Id : removalQueue) {
			config.servers.remove(Id);
		}
		config.save();
	}

	@Override
	@SuppressWarnings({"unchecked", "OptionalGetWithoutIsPresent"})
	public void onGuildMessageReceived (@NotNull GuildMessageReceivedEvent event) {
		BotCommandSource source = new BotCommandSource(event, this);
		ServerSettings settings = config.servers.get(event.getMessage().getGuild().getId());
		String prefix = settings.prefix;
		if (event.getMessage().getContentRaw().startsWith(prefix) && !event.getMessage().getContentRaw().startsWith(prefix.repeat(2))) {
			String messageContentsNoPrefix = event.getMessage().getContentRaw().replaceFirst(prefix.translateEscapes(), "");
			ParseResults<Object> parse = dispatcher.parse(messageContentsNoPrefix, source);
			if (parse.getContext().getCommand() != null) {
				if (parse.getExceptions().isEmpty()) {
					try {
						dispatcher.execute(parse);
					} catch (CommandSyntaxException e) {
						LOGGER.fatal("There's a bug in com.mojang:brigadier; error:", e);
					}
				} else {
					OmenaBot.LOGGER.debug("Failed to parse command {}", Pattern.quote(messageContentsNoPrefix));
					for (Map.Entry<CommandNode<Object>, CommandSyntaxException> exceptionEntry: parse.getExceptions().entrySet()){
						OmenaBot.LOGGER.debug("Exception in node {}: {}", exceptionEntry.getKey() , exceptionEntry.getValue());
					}
					Map<CommandNode<Object>, CommandSyntaxException> e = parse.getExceptions();
					final boolean a[] = {false};
					e.forEach((key, error) -> a[0] |= error.getMessage().startsWith("Unknown command at position "));
					if (a[0]) {
						event.getChannel().sendMessage((e.values()).stream().unordered().findFirst().get().getMessage()).queue();
					}
					LOGGER.debug(messageContentsNoPrefix);
				}
			}
		} else {
			var mentions = event.getMessage().getMentionedMembers();
			if(mentions.size() == 1 && mentions.contains(event.getMember())){
				event.getChannel().sendMessage("Current prefix is [`" + prefix + "`].").queue();
			} else {
				HashMap<String, ServerSettings.Id_s> channels = settings.channels;
				if (channels != null) {
					ServerSettings.Id_s imageOnly = channels.get("image-only");
					if (imageOnly != null) {
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
				LOGGER.debug(event.getMessage());
			}
		}
	}

	public void shutdown () {
		discordApi.shutdown();
	}

	public BotUI getUi () {
		return ui;
	}

	public JDA getApi () {
		return discordApi;
	}

	public static class BotCommandSource {
		final long createdTime = new Date().getTime();
		MessageEvent event;
		private OmenaBot bot;

//		public BotCommandSource (MessageReceivedEvent event, OmenaBot omenaBot) {
//			this.event = new MessageEvent(event);
//			this.bot = omenaBot;
//		}

		public BotCommandSource (GuildMessageReceivedEvent event, OmenaBot omenaBot) {
			this.event = new MessageEvent(event);
			this.bot = omenaBot;
		}

		public long getCreatedTime () {
			return createdTime;
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

		public static class MessageEvent extends Event {

			private Message message;
			private MessageChannel channel;

			public MessageEvent (MessageReceivedEvent event) {
				this(event.getJDA());
				channel = event.getChannel();
				message = event.getMessage();
			}

			public MessageEvent (GuildMessageReceivedEvent event) {
				this(event.getJDA());
				channel = event.getChannel();
				message = event.getMessage();
			}

			public MessageEvent (@NotNull JDA api) {
				super(api);
			}

			public MessageChannel getChannel () {
				return channel;
			}

		}

	}

}
