	package here.lenrik.omenabot.ui;

import javax.swing.*;
import javax.swing.plaf.basic.BasicIconFactory;
import java.awt.*;

public class ConfigPanel extends JPanel {
	public final ResponsesPanel responsesTab;
	public final GeneralSettingsPanel generalTab;
	private final BotUI botUi;
	private final JTabbedPane tabs;

	ConfigPanel (BotUI botUI) {
		setLayout(new BorderLayout());
		this.botUi = botUI;
		responsesTab = new ResponsesPanel(botUI);
		generalTab = new GeneralSettingsPanel(botUI);
		tabs = new JTabbedPane();
		tabs.addTab("Responses", BasicIconFactory.getCheckBoxIcon(), responsesTab, "All the fields for simple commands");
		Image image = Toolkit.getDefaultToolkit().getImage(ConfigPanel.class.getClassLoader().getResource("cog.png"));
		image = image.getScaledInstance(16, 16, 0);
		ImageIcon icon = new ImageIcon(image);
		tabs.addTab("General", icon, generalTab, "General settings (token, devs, pings)");
		add(tabs, BorderLayout.CENTER);
	}

	public void updatetConfig () {
		responsesTab.updateConfig();
		generalTab.updateConfig();
	}

}
