package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.OmenaBot;

import javax.swing.*;
import javax.swing.event.CellEditorListener;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableCellEditor;
import javax.swing.table.TableCellRenderer;
import java.awt.*;
import java.awt.datatransfer.Clipboard;
import java.awt.datatransfer.ClipboardOwner;
import java.awt.datatransfer.StringSelection;
import java.awt.event.ActionEvent;
import java.awt.event.MouseEvent;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.ArrayList;
import java.util.EventObject;
import java.util.List;
import java.util.Objects;

import com.google.common.collect.Lists;
import net.dv8tion.jda.api.Permission;
import net.dv8tion.jda.api.entities.Guild;

import static net.dv8tion.jda.api.Permission.*;

public class InfoPanel extends JTabbedPane {
	final JPanel generalInfo;
	final JPanel status;
	final JLabel members;
	final JLabel guildCount;
	final JLabel state;
	final JButton botInvite;
	private final BotUI botUi;
	Long invitePermissions = ADMINISTRATOR.getRawValue();

	public InfoPanel (BotUI botUI) {
		this.botUi = botUI;
		members = new JLabel("members");
		guildCount = new JLabel("guild");
		state = new JLabel("state");
		status = new JPanel();
		status.setLayout(new BoxLayout(status, BoxLayout.LINE_AXIS));
		status.add(members);
		status.add(guildCount);
		status.add(state);
		JPanel inviteGenerator = new JPanel(new BorderLayout());
		Object[][] perms = {
				{new PermBox(ADMINISTRATOR), /*    */new PermBox(MESSAGE_WRITE), /*       */new PermBox(VOICE_CONNECT)},
				{new PermBox(VIEW_AUDIT_LOGS), /*  */new PermBox(MESSAGE_TTS), /*         */new PermBox(VOICE_SPEAK)},
				{new PermBox(VIEW_GUILD_INSIGHTS), new PermBox(MESSAGE_MANAGE), /*        */new PermBox(VOICE_STREAM)},
				{new PermBox(MANAGE_SERVER), /*    */new PermBox(MESSAGE_EMBED_LINKS), /* */new PermBox(VOICE_MOVE_OTHERS)},
				{new PermBox(MANAGE_ROLES), /*     */new PermBox(MESSAGE_ATTACH_FILES), /**/new PermBox(VOICE_DEAF_OTHERS)},
				{new PermBox(MANAGE_CHANNEL), /*   */new PermBox(MESSAGE_HISTORY), /*     */new PermBox(VOICE_MOVE_OTHERS)},
				{new PermBox(KICK_MEMBERS), /*     */new PermBox(MESSAGE_MENTION_EVERYONE), new PermBox(VOICE_USE_VAD)},
				{new PermBox(BAN_MEMBERS), /*      */new PermBox(MESSAGE_EXT_EMOJI), /*   */new PermBox(PRIORITY_SPEAKER)},
				{new PermBox(CREATE_INSTANT_INVITE), new PermBox(MESSAGE_ADD_REACTION), /**/null},
				{new PermBox(NICKNAME_CHANGE), /*  */null, /*                                          */null},
				{new PermBox(NICKNAME_MANAGE), /*  */null, /*                                          */null},
				{new PermBox(MANAGE_EMOTES), /*    */null, /*                                          */null},
				{new PermBox(MANAGE_WEBHOOKS), /*  */null, /*                                          */null},
				{new PermBox(VIEW_CHANNEL), /*     */null, /*                                          */null},
		};
		String[] columns = {"General Permissions", "Text Permissions", "Voice Permissions"};
		DefaultTableModel model = new DefaultTableModel(perms, columns) {
			@Override
			public Class<?> getColumnClass (int column) {
				return PermBox.class;
			}
		};
		JTable permsTable = new JTable(model);
		permsTable.setDefaultRenderer(PermBox.class, new PermBox(UNKNOWN));
		permsTable.setAutoResizeMode(JTable.AUTO_RESIZE_ALL_COLUMNS);
		permsTable.setDefaultEditor(PermBox.class, new PermBox.PermEditor());
		inviteGenerator.add(new JScrollPane(permsTable), BorderLayout.CENTER);
		inviteGenerator.add(botInvite = new JButton(botUi.getBot() != null ? botUi.getBot().getApi().getInviteUrl() : ""), BorderLayout.SOUTH);
		botInvite.setAction(new AbstractAction() {
			@Override public void actionPerformed (ActionEvent e) {
				String link = ((JButton)e.getSource()).getText();
				getToolkit().getSystemClipboard().setContents(new StringSelection(link), null);
			}
		});
		generalInfo = new JPanel();
		generalInfo.setLayout(new BorderLayout());
		generalInfo.add(status, BorderLayout.NORTH);
		generalInfo.add(inviteGenerator, BorderLayout.CENTER);
		addTab("General", generalInfo);
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

	public void setGuilds (List<Guild> guildsL) {
		ArrayList<String> removalList = Lists.newArrayList();
		for (int i = 1, l = getTabCount(); i < l; i++){
			removalList.add(getTitleAt(i));
		}
		ArrayList<Guild> updateList = new ArrayList<>();
		for (Guild guild : guildsL /*String guild : guildsL.stream().map(Guild::getName).toArray(String[]::new)*/) {
			if (indexOfTab(guild.getName())>0) {
				removalList.remove(guild.getName());
				updateList.add(guild);
			}
		}
		for (String name : removalList) {
			removeTabAt(indexOfTab(name));
		}
		for (Guild guild : guildsL) {
			if (updateList.contains(guild)) {
				((GuildTab) getComponentAt(indexOfTab(guild.getName()))).updateConfig();
			} else {
				final String name = guild.getName();
				try {
					Image image = Toolkit.getDefaultToolkit().getImage(new URL(Objects.requireNonNull(guild.getIconUrl())));
					image = image.getScaledInstance(16, 16, 0);
					ImageIcon icon = new ImageIcon(image);
					addTab(name, icon, new GuildTab(guild, botUi), guild.getId());
				} catch (MalformedURLException | AssertionError | NullPointerException e) {
					addTab(name, null, new GuildTab(guild, botUi), guild.getId());
					OmenaBot.LOGGER.trace(e);
				}
			}
		}
	}

	static class PermBox extends JCheckBox implements TableCellRenderer {
		Permission permission;

		PermBox () {
			this.permission = UNKNOWN;
		}

		PermBox (Permission permission) {
			super(permission.getName(), permission.equals(ADMINISTRATOR));
			this.permission = permission;
			addActionListener(
					message -> {
						InfoPanel panel = (InfoPanel) ((PermBox) message.getSource()).getParent().getParent().getParent().getParent().getParent().getParent();
						Permission.getPermissions(
								panel.invitePermissions ^= ((PermBox) message.getSource()).permission.getRawValue()
						);
						panel.botInvite.setText(panel.botUi.getBot().getApi().getInviteUrl(Permission.getPermissions(panel.invitePermissions)));
					}
			);
		}

		@Override
		public Component getTableCellRendererComponent (JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
			if (value instanceof PermBox) {
				return ((PermBox) value);
			} else {
				return new JLabel(value == null ? "" : value.toString());
			}// ZDYUY2GS
		}

		static class PermEditor implements TableCellEditor {
			PermBox cell = new PermBox();

			public PermEditor () {
			}

			@Override
			public Object getCellEditorValue () {
				return cell.isSelected();
			}

			@Override
			public boolean isCellEditable (EventObject event) {
				return event instanceof MouseEvent;
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
				return value instanceof PermBox ? (PermBox) value : new JLabel(value == null ? "" : value.toString());
			}

		}

	}

}
