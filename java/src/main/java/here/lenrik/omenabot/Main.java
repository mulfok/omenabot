package here.lenrik.omenabot;

import here.lenrik.omenabot.config.ConfigManager;
import here.lenrik.omenabot.ui.BotUI;

import javax.security.auth.login.LoginException;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Main {
	public static Logger LOGGER = LogManager.getLogger("");
	public static OmenaBot bot;
	public static BotUI ui;

	public static void main (String... args) {
		ConfigManager configManager = new ConfigManager();
		configManager.load(System.getProperty("user.dir"));
		ui = new BotUI();
		try {
			LOGGER.info("Setting up the bot");
			bot = new OmenaBot(configManager, ui);
			ui.setBot(bot);
		} catch (LoginException e) {
			System.out.println("Login failed.");
			System.exit(1);
		}
	}

}
