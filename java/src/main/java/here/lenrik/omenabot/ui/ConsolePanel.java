package here.lenrik.omenabot.ui;

import javax.swing.*;
import javax.swing.text.BadLocationException;
import javax.swing.text.JTextComponent;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.io.IOException;
import java.io.StringReader;
import java.io.Writer;

import org.apache.logging.log4j.Level;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.Appender;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.appender.WriterAppender;
import org.apache.logging.log4j.core.config.Configuration;
import org.apache.logging.log4j.core.layout.PatternLayout;
import org.jetbrains.annotations.NotNull;

public class ConsolePanel extends JPanel {
	final BotUI botUi;
	final JPanel buttonPanel;
	final JButton kill;
	final JButton send;
	final JTextPane textPane;
	final JTextField input;

	ConsolePanel (BotUI botUI) {
		this.botUi = botUI;
		// add this tab's console appender;
		final LoggerContext ctx = (LoggerContext) LogManager.getContext(false);
		final Configuration config = ctx.getConfiguration();
		PatternLayout.Builder paB = PatternLayout.newBuilder();
		paB.withPattern("[%d] [%t|%logger{36}/%-5p] %m%n");
		paB.withConfiguration(config);
		var t = WriterAppender.newBuilder();
		t.setLayout(paB.build());
		textPane = new JTextPane();
		t.setTarget(new ConsoleWriter(textPane));
		t.setName("UI Console");
		Appender appender = t.build();
		appender.start();
		config.addAppender(appender);
		config.getLoggerConfig("").addAppender(appender, Level.ALL, null);
		ctx.updateLoggers();

		setLayout(new BorderLayout());
		JPanel controls = new JPanel(new BorderLayout());
		input = new JFormattedTextField();
		send = new JButton("send");
		send.addActionListener(this::buttonPressed);
		kill = new JButton("kill");
		kill.addActionListener(this::buttonPressed);
		kill.setBackground(new Color(199, 39, 24));
		buttonPanel = new JPanel();
		buttonPanel.add(send);
		buttonPanel.add(kill);
		buttonPanel.setLayout(new BoxLayout(buttonPanel, BoxLayout.LINE_AXIS));
		controls.add(input, BorderLayout.NORTH);
		controls.add(buttonPanel, BorderLayout.SOUTH);
		textPane.enableInputMethods(false);
		textPane.setEditable(false);
		JScrollPane textPaneContainer = new JScrollPane(textPane);
		textPaneContainer.setVerticalScrollBarPolicy(JScrollPane.VERTICAL_SCROLLBAR_ALWAYS);
		add(textPaneContainer, BorderLayout.CENTER);
		add(controls, BorderLayout.SOUTH);
		doLayout();
		JFrame.setDefaultLookAndFeelDecorated(true);
	}

	public void buttonPressed (ActionEvent event) {
		switch (event.getActionCommand()) {
			case "kill" -> this.botUi.dispose();
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

	static public class ConsoleWriter extends Writer {

		private final JTextComponent console;

		public ConsoleWriter (JTextPane textPane) {
			console = textPane;
		}

		@Override
		public void write (@NotNull char[] cbuf, int off, int len) throws IOException {
			console.setEditable(true);
			console.read(new StringReader(console.getText() +
					String.copyValueOf(cbuf, off, len)), null
			);
			console.setEditable(false);
		}

		@Override
		public void flush () throws IOException {

		}

		@Override
		public void close () throws IOException {

		}

	}


}
