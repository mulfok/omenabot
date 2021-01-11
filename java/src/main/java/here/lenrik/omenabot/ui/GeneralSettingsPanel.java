package here.lenrik.omenabot.ui;

import javax.swing.*;
import java.awt.*;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.sql.Time;

import org.apache.logging.log4j.LogManager;

public class GeneralSettingsPanel extends JPanel {
	private final BotUI botUi;
	private final JPasswordField tokenField;
	char hiddenChar;

	GeneralSettingsPanel (BotUI botUI) {
		setLayout(new BorderLayout());
		this.botUi = botUI;
		tokenField = new JPasswordField();
		JButton revealTokenButton = new JButton("Reveal TOKEN");
		revealTokenButton.addMouseListener(new MouseAdapter() {
			@Override
			public void mousePressed (MouseEvent event) {
				hiddenChar = tokenField.getEchoChar();
				LogManager.getLogger(event.getSource().getClass().getName()).info("Token revealed at {}", new Time(event.getWhen()));
				tokenField.setEchoChar((char) 0);

			}

			@Override
			public void mouseReleased (MouseEvent event) {
				LogManager.getLogger(event.getSource().getClass().getName()).info("Token hidden at {}", new Time(event.getWhen()));
				tokenField.setEchoChar(hiddenChar);
			}
		});
		JPanel tokenPane = new JPanel();
		tokenPane.add(tokenField);
		tokenPane.add("reveal token button", revealTokenButton);
		add(tokenPane, BorderLayout.NORTH);
	}

	public void updateConfig () {
		tokenField.setText(botUi.getBot().config.botSettings.token);
	}

}
