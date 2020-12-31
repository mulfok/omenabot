package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.OmenaBot;

import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.beans.PropertyChangeListener;

import org.apache.logging.log4j.LogManager;

public class BotUI extends JFrame {
	public ConsolePanel consoleTab;
	public InfoPanel infoPane;
	public JMenuBar menuBar;
	public JTabbedPane tabs;
	public JMenu fileMenu;
	private OmenaBot bot;

	public BotUI () {
		// /usr/lib/jvm/java-1.14.0-openjdk-amd64/bin/java
		//  -javaagent:
		// /home/tent/Downloads/idea-IC-201.8743.12/lib/idea_rt.jar=35273:
		// /home/tent/Downloads/idea-IC-201.8743.12/bin
		//  -Dfile.encoding=UTF-8
		//  -classpath
		//  /tmp/FormPreview:
		// /home/tent/Downloads/idea-IC-201.8743.12/lib/forms-1.1-preview.jar:
		// /media/tent/ehh/omenabot/java/src/main/java:
		// /media/tent/ehh/omenabot/java/src/main/resources:
		// /media/tent/ehh/omenabot/java/build/classes/java/main:
		// /media/tent/ehh/omenabot/java/build/resources/main:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.mojang/brigadier/1.0.500/498de4a6f9e1997f322ec29503084d98e2a5a29b/brigadier-1.0.500.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-core/2.14.0/e257b0562453f73eabac1bc3181ba33e79d193ed/log4j-core-2.14.0.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-api/2.14.0/23cdb2c6babad9b2b0dcf47c6a2c29d504e4c7a8/log4j-api-2.14.0.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.google.code.gson/gson/2.8.6/9180733b7df8542621dc12e21e87557e8c99b8cb/gson-2.8.6.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/net.dv8tion/JDA/4.2.0_218/18fff9963aadb71171547d820d5233dac3d8ba57/JDA-4.2.0_218.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.google.guava/guava/21.0/3a3d111be1be1b745edfa7d91678a12d7ed38709/guava-21.0.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.google.code.findbugs/jsr305/3.0.2/25ea2e8b0c338a877313bd4672d3fe056ea78f0d/jsr305-3.0.2.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/org.jetbrains/annotations/16.0.1/c1a6655cebcac68e63e4c24d23f573035032eb2a/annotations-16.0.1.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/org.slf4j/slf4j-api/1.7.25/da76ca59f6a57ee3102f8f9bd9cee742973efa8a/slf4j-api-1.7.25.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.neovisionaries/nv-websocket-client/2.10/4309de0f0ba90e77f14bf9dd1a43c163d9541e70/nv-websocket-client-2.10.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.squareup.okhttp3/okhttp/3.13.0/f53f6362226e4546c3987b8693f3d6976df8c797/okhttp-3.13.0.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/club.minnced/opus-java/1.0.4/596995aaf2f5b5091c4d251fdc11fa62680cc59e/opus-java-1.0.4.pom:
		// /home/tent/.gradle/caches/modules-2/files-2.1/org.apache.commons/commons-collections4/4.1/a4cf4688fe1c7e3a63aa636cc96d013af537768e/commons-collections4-4.1.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.squareup.okio/okio/1.17.2/78c7820b205002da4d2d137f6f312bd64b3d6049/okio-1.17.2.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/club.minnced/opus-java-api/1.0.4/20e4fafa8523ed391446ddc7dff60ef832f1543a/opus-java-api-1.0.4.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/club.minnced/opus-java-natives/1.0.4/292d015243833578eda04b1ad0af2dc351b14b1b/opus-java-natives-1.0.4.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/net.sf.trove4j/trove4j/3.0.3/42ccaf4761f0dfdfa805c9e340d99a755907e2dd/trove4j-3.0.3.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.fasterxml.jackson.core/jackson-databind/2.10.1/18eee15ffc662d27538d5b6ee84e4c92c0a9d03e/jackson-databind-2.10.1.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.fasterxml.jackson.core/jackson-annotations/2.10.1/54d72475c0d6819f2d0e9a09d25c3ed876a4972f/jackson-annotations-2.10.1.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/com.fasterxml.jackson.core/jackson-core/2.10.1/2c8b5e26ba40e5f91eb37a24075a2028b402c5f9/jackson-core-2.10.1.jar:
		// /home/tent/.gradle/caches/modules-2/files-2.1/net.java.dev.jna/jna/4.4.0/cb208278274bf12ebdb56c61bd7407e6f774d65a/jna-4.4.0.jar
		//  com.intellij.uiDesigner.FormPreviewFrame
		// "The silence Vill fall!"
		// "Can you hear the silence"
		LookAndFeel lookAndFeel = new LookAndFeel() {
			@Override
			public String getName () {
				return null;
			}

			@Override
			public String getID () {
				return null;
			}

			@Override
			public String getDescription () {
				return null;
			}

			@Override
			public boolean isNativeLookAndFeel () {
				return false;
			}

			@Override
			public boolean isSupportedLookAndFeel () {
				return false;
			}
		};
		setDefaultLookAndFeelDecorated(true);
		setBackground(backgroundColor);
		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		menuBar = this.rootPane.getJMenuBar();
		if (menuBar == null) {
			menuBar = new JMenuBar();
		}
		menuBar.setBackground(backgroundColor);
		setJMenuBar(menuBar);
		fileMenu = new JMenu("file");
		menuBar.add(fileMenu);

		consoleTab = new ConsolePanel();
		infoPane = new InfoPanel();
		tabs = new JTabbedPane();
		tabs.addTab("Desktop", infoPane);
		tabs.addTab("Console", consoleTab);
		setContentPane(tabs);
		setSize(400, 400);
		setVisible(true);
	}

	@Override
	public void dispose () {
		super.dispose();
		bot.shutdown();
	}

	@SuppressWarnings("unused")
	public void setInfo () {

	}

	public void setBot (OmenaBot bot) {
		this.bot = bot;
	}

	@SuppressWarnings("unused")
	public OmenaBot getBot () {
		return bot;
	}

	public static final Color backgroundColor = new Color(56, 56, 56);
	public static class ConsolePanel extends JPanel {
		JPanel buttonPanel;
		JButton kill;
		JButton send;
		JTextPane textPane;
		JTextField input;

		ConsolePanel () {
			setBackground(backgroundColor);
			setLayout(new GridLayout(1 + 1, 1));
			input = new JFormattedTextField();
			input.setBackground(backgroundColor);
			send = new JButton("send");
			send.setBackground(backgroundColor);
			kill = new JButton("kill");
			kill.setBackground(backgroundColor);
			kill.setAction(new KillAction());
			buttonPanel = new JPanel();
			buttonPanel.setBackground(backgroundColor);
			buttonPanel.add(input);
			buttonPanel.add(send);
			buttonPanel.add(kill);
			buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.PAGE_AXIS));
			textPane = new JTextPane();
			textPane.setBackground(backgroundColor);
			textPane.setAlignmentY(0);
			add(textPane);
			add(buttonPanel);
			doLayout();
			setDefaultLookAndFeelDecorated(true);
		}

		public static class KillAction implements Action {

			private boolean enabled = true;

			@Override
			public Object getValue (String s) {
				return null;
			}

			@Override
			public void putValue (String s, Object o) {

			}

			@Override
			public void setEnabled (boolean b) {
				enabled = b;
			}

			@Override
			public boolean isEnabled () {
				return enabled;
			}

			@Override
			public boolean accept (Object sender) {
				LogManager.getLogger("button").info("button pressed, caller: {} ({})", sender, sender.getClass());
				return false;
			}

			@Override
			public void addPropertyChangeListener (PropertyChangeListener propertyChangeListener) {

			}

			@Override
			public void removePropertyChangeListener (PropertyChangeListener propertyChangeListener) {

			}

			@Override
			public void actionPerformed (ActionEvent actionEvent) {

			}

		}

	}

	public static class InfoPanel extends JPanel {
		JLabel members;
		JLabel guilds;
		JLabel state;

		public InfoPanel () {
			setBackground(new Color(56, 56, 56));
			members = new JLabel("members");
			guilds = new JLabel("guild");
			state = new JLabel("state");
			this.add(members);
			this.add(guilds);
			this.add(state);
		}

		public void setMembers (String text) {
			members.setText(text);
		}

		public void setGuilds (String text) {
			guilds.setText(text);
		}

		public void setState (String text) {
			state.setText(text);
		}

	}

}
