package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.OmenaBot;

import javax.swing.*;
import java.awt.*;

import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.events.GenericEvent;

public class BotUI extends JFrame {
	public static final Color backgroundColor = new Color(56, 56, 56);
	public static final Color foregroundColor = new Color(164, 164, 169);
	public static final Color lineColor = new Color(44, 44, 44);
	public final ConfigPanel configTab;
	public final ConsolePanel consoleTab;
	public final InfoPanel infotab;
	public final JTabbedPane tabs;
	public final JMenu fileMenu;
	public JMenuBar menuBar;
	private OmenaBot bot;

	public BotUI () {
		//		SynthLookAndFeel laf = new SynthLookAndFeel();
		//		try {
		//			laf.load(this.getClass().getClassLoader().getResource("laf.xml"));
		//			UIManager.setLookAndFeel(laf);
		//		} catch (ParseException | UnsupportedLookAndFeelException | IOException e) {
		//			e.printStackTrace();
		//		}
		setDefaultLookAndFeelDecorated(true);
		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		menuBar = this.rootPane.getJMenuBar();
		if (menuBar == null) {
			menuBar = new JMenuBar();
		}
		setJMenuBar(menuBar);
		fileMenu = new JMenu("file");
		menuBar.add(fileMenu);

		consoleTab = new ConsolePanel(this);
		infotab = new InfoPanel(this);
		configTab = new ConfigPanel(this);
		tabs = new JTabbedPane();
		tabs.addTab("Info", infotab);
		tabs.addTab("Console", consoleTab);
		tabs.addTab("Configs", null, configTab, "All the configs");
		JPanel content = new JPanel(new BorderLayout());
		content.add(tabs, BorderLayout.CENTER);
		setContentPane(content);
		setSize(600, 400);
		setVisible(true);
	}

	@Override
	public void dispose () {
		super.dispose();
		bot.shutdown();
	}

	public OmenaBot getBot () {
		return bot;
	}

	public void setBot (OmenaBot bot) {
		this.bot = bot;
		configTab.updatetConfig();
	}

	public void updateStatus (GenericEvent event) {
		int memberCount = 0;
		for (Guild guild : event.getJDA().getGuilds()) {
			memberCount += guild.getMemberCount();
		}
		infotab.setMembers(memberCount + " members.");
		infotab.setGuildCount(event.getJDA().getGuilds().size() + " guilds (" + (event.getJDA().getGuilds().size() - event.getJDA().getUnavailableGuilds().size()) + "/" + event.getJDA().getUnavailableGuilds().size() + ")");
		infotab.setState("state: '" + event.getJDA().getStatus().name() + "'");
		infotab.setGuilds(event.getJDA().getGuilds());
		consoleTab.updateStatus(event);
	}

}
