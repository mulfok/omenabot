package here.lenrik.omenabot.ui;

import here.lenrik.omenabot.config.Responses;

import javax.swing.*;
import javax.swing.tree.DefaultMutableTreeNode;
import javax.swing.tree.TreeNode;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class ResponsesPanel extends JPanel implements ActionListener {
	private static final String ADD_COMMAND = "add";
	private static final String REMOVE_COMMAND = "remove";
	private static final String CLEAR_COMMAND = "clear";
	private static final String SAVE_COMMAND = "save";
	private static final String RELOAD_COMMAND = "reload";

	private final DynamicTree responses;
	private final BotUI botUi;
	private final DefaultMutableTreeNode f;
	private final DefaultMutableTreeNode anime;
	private final DefaultMutableTreeNode jokes;
	private final DefaultMutableTreeNode _8ball;
	private final DefaultMutableTreeNode trivia;
	private final DefaultMutableTreeNode pong_win;
	private final DefaultMutableTreeNode pong_loss;
	private final DefaultMutableTreeNode mc_commands;
	private final DefaultMutableTreeNode hack_payment;
	private final DefaultMutableTreeNode hack_homework;
	private final DefaultMutableTreeNode hack_mail_body;
	private final DefaultMutableTreeNode hack_companies;
	private final DefaultMutableTreeNode hack_mail_provider;
	private Responses config;

	public ResponsesPanel (BotUI botUi) {
		super(new BorderLayout());
		this.botUi = botUi;
		responses = new DynamicTree("responses");
		responses.protectNode(f = responses.addObject("f"));
		DefaultMutableTreeNode hack;
		responses.protectNode(hack = responses.addObject("hack"));
		responses.protectNode(anime = responses.addObject("anime"));
		responses.protectNode(jokes = responses.addObject("jokes"));
		responses.protectNode(_8ball = responses.addObject("8ball"));
		responses.protectNode(trivia = responses.addObject("trivia"));
		responses.protectNode(pong_win = responses.addObject("pong win"));
		responses.protectNode(pong_loss = responses.addObject("pong loss"));
		responses.protectNode(mc_commands = responses.addObject("mc commands"));
		responses.protectNode(hack_payment = responses.addObject(hack, "payment"));
		responses.protectNode(hack_homework = responses.addObject(hack, "homework"));
		responses.protectNode(hack_companies = responses.addObject(hack, "companies"));
		responses.protectNode(hack_mail_body = responses.addObject(hack, "mail_body"));
		responses.protectNode(hack_mail_provider = responses.addObject(hack, "mail_provider"));

		add(responses, BorderLayout.CENTER);

		JButton add = new JButton("Add");
		add.setActionCommand(ADD_COMMAND);
		add.addActionListener(this);

		JButton remove = new JButton("Remove");
		remove.setActionCommand(REMOVE_COMMAND);
		remove.addActionListener(this);

		JButton clear = new JButton("Clear");
		clear.setActionCommand(CLEAR_COMMAND);
		clear.addActionListener(this);

		JButton save = new JButton("Save");
		save.setActionCommand(SAVE_COMMAND);
		save.addActionListener(this);

		JButton reload = new JButton("Reload");
		reload.setActionCommand(RELOAD_COMMAND);
		reload.addActionListener(this);

		JPanel panel = new JPanel(new GridLayout(0, 5));
		panel.add(add);
		panel.add(save);
		panel.add(clear);
		panel.add(reload);
		panel.add(remove);
		add(panel, BorderLayout.SOUTH);
	}

	@Override
	public void actionPerformed (ActionEvent e) {
		String command = e.getActionCommand();
		switch (command) {
			case RELOAD_COMMAND -> updateConfig();
			case SAVE_COMMAND -> {
				config.f.clear();
				for (TreeNode child : Collections.list(f.children())) {
					config.f.add((String) ((DefaultMutableTreeNode) child).getUserObject());
				}
			}
			//Add button clicked
			case ADD_COMMAND -> responses.addObject("");
			//Remove button clicked
			case REMOVE_COMMAND -> responses.removeCurrentNode();
			//Clear button clicked.
			case CLEAR_COMMAND -> responses.clear();
		}
	}

	public void updateConfig () {
		config = botUi.getBot().config.responses;
		f.removeAllChildren();
		anime.removeAllChildren();
		jokes.removeAllChildren();
		_8ball.removeAllChildren();
		trivia.removeAllChildren();
		pong_win.removeAllChildren();
		pong_loss.removeAllChildren();
		mc_commands.removeAllChildren();
		hack_payment.removeAllChildren();
		hack_homework.removeAllChildren();
		hack_companies.removeAllChildren();
		hack_mail_body.removeAllChildren();
		hack_mail_provider.removeAllChildren();
		for (String f : config.f) {
			responses.addObject(this.f, f).setAllowsChildren(false);
		}
		for (String ball : config._8ball) {
			responses.addObject(_8ball, ball).setAllowsChildren(false);
		}
		for (Responses.Joke joke : config.jokes) {
			responses.addObject(responses.addObject(jokes, joke.joke), joke.punchline).setAllowsChildren(false);
		}
		for (String fact : config.trivia) {
			responses.addObject(trivia, fact).setAllowsChildren(false);
		}
		for (String win : config.pong_win) {
			responses.addObject(pong_win, win).setAllowsChildren(false);
		}
		for (String loss : config.pong_loss) {
			responses.addObject(pong_loss, loss).setAllowsChildren(false);
		}
		for (String anime : config.anime) {
			responses.addObject(this.anime, anime).setAllowsChildren(false);
		}
		for (String payment : config.hack.payment) {
			responses.addObject(hack_payment, payment).setAllowsChildren(false);
		}
		for (String size : config.hack.homework) {
			responses.addObject(hack_homework, size).setAllowsChildren(false);
		}
		for (String company : config.hack.companies) {
			responses.addObject(hack_companies, company).setAllowsChildren(false);
		}
		for (String provider : config.hack.mail_provider) {
			responses.addObject(hack_mail_provider, provider).setAllowsChildren(false);
		}
		for (ArrayList<String> body : config.hack.mail_body) {
			responses.addObject(hack_mail_body, body.get(0) + ":" + body.get(1));
		}
		for (Map.Entry<String, HashMap<String, String>> version : config.mc_commands.entrySet()) {
			DefaultMutableTreeNode versionNode = responses.addObject(mc_commands, version.getKey());
			for (Map.Entry<String, String> command : version.getValue().entrySet()) {
				responses.addObject(responses.addObject(versionNode, command.getKey()), command.getValue()).setAllowsChildren(false);
			}
		}
	}

}
