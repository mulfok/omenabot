package here.lenrik.omenabot;

import here.lenrik.omenabot.config.ConfigManager;
import here.lenrik.omenabot.ui.BotUI;

import javax.security.auth.login.LoginException;
import javax.swing.*;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Main {
	public static final Logger LOGGER = LogManager.getLogger("");
	public static OmenaBot bot;
	public static BotUI ui;

	public static void main (String... args) {
		LOGGER.debug("loading configs");
		ConfigManager configManager = new ConfigManager();
		configManager.load(System.getProperty("user.dir"));
		String tokenName = System.getProperty("omenabot.token_name", "test bot");

		LOGGER.debug("starting UI");
		ui = new BotUI();
		try {
			LOGGER.info("Setting up the bot");
			bot = new OmenaBot(configManager, ui, tokenName);
			ui.setBot(bot);
		} catch (LoginException e) {
			LOGGER.trace(e);
			System.exit(1);
		}
	}

}
