package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.OmenaBot;
import here.lenrik.omenabot.config.ServerSettings;

import javax.swing.*;
import javax.swing.event.CellEditorListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellEditor;
import javax.swing.text.TextAction;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.KeyAdapter;
import java.awt.event.KeyEvent;
import java.awt.event.MouseEvent;
import java.util.EventObject;
import java.util.Map;

import net.dv8tion.jda.api.entities.Guild;
import net.dv8tion.jda.api.entities.Member;
import net.dv8tion.jda.api.exceptions.ErrorResponseException;

public class GuildTab extends JPanel {
	private final ServerSettings settings;
	private final BotUI botUi;
	private final JTextField prefixField;
	private final JLabel membersLabel;
	private final JTable nicks;
	private Guild apiGuild;

	public GuildTab (final Guild guild, BotUI botUi) {
		this.botUi = botUi;
		this.setLayout(new BorderLayout());
		this.apiGuild = guild;
		add(new JLabel("ID: " + apiGuild.getId()));
		JPanel membersPanel = new JPanel();
		{
			membersPanel.add(new JLabel("Members: "));
			membersPanel.add(membersLabel = new JLabel(String.valueOf(guild.getMemberCount())));
			this.add(membersPanel);
		}
		settings = botUi.getBot().config.servers.get(apiGuild.getId());
		JPanel prefixPanel = new JPanel();
		{
			prefixPanel.add(new JLabel("Prefix: "));
			prefixField = new JTextField("");
			prefixField.addActionListener((action) -> {
				OmenaBot.LOGGER.info(action.getActionCommand());
				((GuildTab) ((JTextField) action.getSource()).getParent().getParent()).settings.prefix = action.getActionCommand();
				((GuildTab) ((JTextField) action.getSource()).getParent().getParent()).botUi.getBot().config.save(System.getProperty("user.dir") + "/test");
			});
			prefixField.addKeyListener(new KeyAdapter() {
				@Override
				public void keyTyped (KeyEvent event) {
					super.keyTyped(event);
					((JPanel) ((JTextField) event.getSource()).getParent()).updateUI();
				}
			});
			prefixPanel.add(prefixField);
			add(prefixPanel, BorderLayout.NORTH);
		}
		JPopupMenu menu = new JPopupMenu();
		{
			menu.add(new TextAction("add") {
				public void actionPerformed (ActionEvent e) {OmenaBot.LOGGER.info(((JComponent)e.getSource()).getParent());}
			});
			setComponentPopupMenu(menu);
		}

		JPanel listsPane = new JPanel(new BorderLayout());
		nicks = new JTable(new DefaultTableModel(new String[]{"Username", "Permanent Nickname"}, 0) {
			@Override
			public Class<?> getColumnClass (int columnIndex) {
				if (columnIndex == 0) {
					return Member.class;
				} else {
					return super.getColumnClass(columnIndex);
				}
			}
		});
		nicks.setDefaultRenderer(Member.class, (table, value, isSelected, hasFocus, row, column) -> {
			GuildTab origin = (GuildTab) table.getParent().getParent().getParent().getParent().getParent().getParent();
			Member member = guild.getMemberById(value.toString()) == null ? guild.retrieveMemberById(value.toString()).complete() : guild.getMemberById(value.toString());
			try {
				final JLabel label = new JLabel(member.getUser().getName());
				if (hasFocus) {
					if (isSelected) {
						label.setBorder(UIManager.getBorder("Table.focusSelectedCellHighlightBorder"));
					} else {
						label.setBorder(UIManager.getBorder("Table.focusCellHighlightBorder"));
						if (table.isCellEditable(row, column)) {
							Color col;
							if ((col = UIManager.getColor("Table.focusCellForeground")) != null) {
								label.setForeground(col);
							}
							if ((col = UIManager.getColor("Table.focusCellBackground")) != null) {
								label.setBackground(col);
							}
						}
					}
				}
				return label;
			} catch (IllegalArgumentException e) {
				return new JLabel("iae");
			} catch (NullPointerException e) {
				return new JLabel("npe");
			} catch (ErrorResponseException e) {
				switch (e.getErrorCode()){
					case 0 -> OmenaBot.LOGGER.trace(e);
					case 10013 -> OmenaBot.LOGGER.info(
							"User {} is not valid",
							guild.getJDA().getUserById(value.toString()) == null?(guild.getJDA().retrieveUserById(value.toString()).complete()) :(guild.getJDA().getUserById(value.toString()))
					);
					case 10007 -> {
						OmenaBot.LOGGER.info(
								"User {} is no longer a member of guild {}",
								guild.getJDA().getUserById(value.toString()) == null? guild.getJDA().retrieveUserById(value.toString()).complete() : guild.getJDA().getUserById(value.toString()),
								guild
						);
						origin.botUi.getBot().config.servers.get(guild.getId()).nicks.remove(value.toString());
						origin.botUi.getBot().config.save();
						return new Label("Deleting");
					}
				}
				return new Label(e.getMessage());
			}
		});
		nicks.setDefaultRenderer(String.class, ((table, value, isSelected, hasFocus, row, column) -> {
			JLabel label = new JLabel(value.toString());
			label.setFont(new Font("Exo" + (1 + 1), Font.PLAIN, 14));
			return label;
		}));
		nicks.setDefaultEditor(Member.class, new TableCellEditor(){
			JTextField cell = new JTextField();

			@Override
			public Object getCellEditorValue () {
				return guild.getMemberById(cell.getText());
			}

			@Override
			public boolean isCellEditable (EventObject event) {
				return event instanceof MouseEvent && ((MouseEvent) event).getClickCount() > 1;
			}

			@Override
			public boolean shouldSelectCell (EventObject event) {
				return event instanceof MouseEvent;
			}

			@Override
			public boolean stopCellEditing () {
				return true;
			}

			@Override
			public void cancelCellEditing () {

			}

			@Override
			public void addCellEditorListener (CellEditorListener l) {

			}

			@Override
			public void removeCellEditorListener (CellEditorListener l) {

			}
			@Override
			public Component getTableCellEditorComponent (JTable table, Object value, boolean isSelected, int row, int column) {
				return cell = new JTextField(value.toString());
			}
		});
		nicks.setComponentPopupMenu(menu);
		final JScrollPane nicksPane = new JScrollPane(nicks);
		listsPane.add(nicksPane, BorderLayout.NORTH);
		JTable channelsTable = new JTable(new DefaultTableModel(new String[]{"channel", "channels"}, 0));
//		channelsTable.setDefaultRenderer();
		channelsTable.setComponentPopupMenu(menu);
		listsPane.add(new JScrollPane(channelsTable), BorderLayout.CENTER);
		add(new JScrollPane(listsPane));
		updateConfig();
	}

	public void updateConfig () {
		apiGuild = botUi.getBot().getApi().getGuildById(apiGuild.getId());
		if (settings != null) {
			if (prefixField != null) {
				prefixField.setText(settings.prefix);
			}
			if (settings.nicks != null && settings.nicks.size() > 0) {
				if (nicks != null) {
					while (nicks.getModel().getRowCount() > 0) {
						((DefaultTableModel) nicks.getModel()).removeRow(0);
					}
					for (Map.Entry<String, String> entry : settings.nicks.entrySet()) {
						((DefaultTableModel) nicks.getModel()).addRow(new String[]{entry.getKey(), entry.getValue()});
					}
				}
			}
		}
		membersLabel.setText(String.valueOf(apiGuild.getMemberCount()));
	}

}
