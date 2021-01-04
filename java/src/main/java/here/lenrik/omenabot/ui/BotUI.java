package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.OmenaBot;

import javax.swing.*;
import javax.swing.plaf.synth.SynthLookAndFeel;
import javax.swing.text.BadLocationException;
import javax.swing.tree.DefaultTreeCellRenderer;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.net.URL;
import java.text.ParseException;
import java.util.ArrayList;

import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.events.GenericEvent;
import org.apache.logging.log4j.LogManager;

public class BotUI extends JFrame {
	DefaultTreeCellRenderer renderer;
	public final ResponsesPanel responsesTab;
	public final ConsolePanel consoleTab;
	public final InfoPanel infotab;
	public JMenuBar menuBar;
	public final JTabbedPane tabs;
	public final JMenu fileMenu;
	private OmenaBot bot;

	public BotUI () {
		SynthLookAndFeel laf = new SynthLookAndFeel();
		try {
			laf.load(new URL("laf.xml"));
			UIManager.setLookAndFeel(laf);
		} catch (ParseException | UnsupportedLookAndFeelException | IOException e) {
			e.printStackTrace();
		}
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
		infotab = new InfoPanel();
		responsesTab = new ResponsesPanel(this);
		tabs = new JTabbedPane();
		tabs.addTab("Info", infotab);
		tabs.addTab("Console", consoleTab);
		tabs.addTab("Responses", responsesTab);
		setContentPane(tabs);
		setSize(400, 400);
		setVisible(true);
	}

	@Override
	public void dispose () {
		super.dispose();
		bot.shutdown();
	}

	public void setBot (OmenaBot bot) {
		this.bot = bot;
		responsesTab.updateConfig();
	}

	public OmenaBot getBot () {
		return bot;
	}

	public static final Color backgroundColor = new Color(56, 56, 56);
	public static final Color foregroundColor = new Color(164, 164, 169);
	public static final Color lineColor = new Color(44, 44, 44);

	public void updateStatus (GenericEvent event) {
		int memberCount = 0;
		for (Guild guild : event.getJDA().getGuilds()) {
			memberCount += guild.getMemberCount();
		}
		infotab.setMembers(memberCount + " members.");
		infotab.setGuildCount(event.getJDA().getGuilds().size() + " guilds (" + (event.getJDA().getGuilds().size() - event.getJDA().getUnavailableGuilds().size()) + "/" + event.getJDA().getUnavailableGuilds().size() + ")");
		infotab.setState("state: '" + event.getJDA().getStatus().name() + "'");
		StringBuilder builder = new StringBuilder();
		for (Guild guild : event.getJDA().getGuilds()) {
			builder.append("\n").append(guild);
		}
		infotab.setGuilds(builder.toString());
	}

	public static class ConsolePanel extends JPanel {
		final BotUI UI;
		final JPanel buttonPanel;
		final JButton kill;
		final JButton send;
		final JTextPane textPane;
		final JTextField input;

		ConsolePanel (BotUI ui) {
			this.UI = ui;
			setLayout(new GridLayout(1 + 1, 1));
			input = new JFormattedTextField();
			send = new JButton("send");
			send.addActionListener(this::buttonPressed);
			kill = new JButton("kill");
			kill.addActionListener(this::buttonPressed);
			buttonPanel = new JPanel();
			buttonPanel.add(input);
			buttonPanel.add(send);
			buttonPanel.add(kill);
			buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.PAGE_AXIS));
			textPane = new JTextPane();
			textPane.setAlignmentY(0);
			add(textPane);
			add(buttonPanel);
			doLayout();
			setDefaultLookAndFeelDecorated(true);
		}

		public void buttonPressed (ActionEvent event) {
			switch (event.getActionCommand()) {
				case "kill" -> this.UI.dispose();
				case "send" -> {
					try {
						LogManager.getLogger("button").info(input.getDocument().getText(0, input.getDocument().getLength()));
					} catch (BadLocationException e) {
						e.printStackTrace();
					} finally {
						input.setText("");
					}
				}
			}
		}

	}

	public static class InfoPanel extends JPanel {
		final JLabel members;
		final JLabel guildCount;
		final JLabel state;
		final JPanel guilds;
		final GridBagConstraints gbc;
		final ArrayList<JLabel> guildLabels = new ArrayList<>();

		public InfoPanel () {
			members = new JLabel("members");
			guildCount = new JLabel("guild");
			guilds = new JPanel();
			guilds.setLayout(new BoxLayout(guilds, BoxLayout.PAGE_AXIS));
			gbc = new GridBagConstraints();
			state = new JLabel("state");
			this.add(members);
			this.add(guildCount);
			this.add(state);
			this.add(guilds);
		}

		public void setMembers (String text) {
			members.setText(text);
		}

		public void setGuildCount (String text) {
			guildCount.setText(text);
		}

		public void setState (String text) {
			state.setText(text);
		}

		public void setGuilds (String text) {
			for (JLabel label : guildLabels) {
				guilds.remove(label);
			}
			for (String line : text.split("\n")) {
				JLabel label = new JLabel(line);
				guilds.add(label, gbc);
				guildLabels.add(label);
			}
		}

	}

}
