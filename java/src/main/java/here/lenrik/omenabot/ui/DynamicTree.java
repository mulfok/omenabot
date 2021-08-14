package here.lenrik.omenabot.ui;

import javax.swing.*;
import javax.swing.event.TreeModelEvent;
import javax.swing.event.TreeModelListener;
import javax.swing.tree.*;
import java.awt.*;
import java.util.ArrayList;
import java.util.Collections;

import org.apache.logging.log4j.LogManager;

public class DynamicTree extends JPanel {
	private final Toolkit toolkit = Toolkit.getDefaultToolkit();
	protected DefaultMutableTreeNode rootNode;
	protected DefaultTreeModel model;
	protected JTree tree;
	protected ArrayList<TreeNode> protectedNodes = new ArrayList<>();

	public DynamicTree () {
		this("Root Node");
	}

	public DynamicTree (Object rootNode) {
		this(new DefaultMutableTreeNode(rootNode));
	}

	public DynamicTree (DefaultMutableTreeNode rootNode) {
		super(new GridLayout());
		this.rootNode = rootNode;
		protectNode(rootNode);

		model = new DefaultTreeModel(rootNode);
		model.addTreeModelListener(new MyTreeModelListener());
		tree = new JTree(model);
		tree.setEditable(true);
		tree.getSelectionModel().setSelectionMode(TreeSelectionModel.SINGLE_TREE_SELECTION);
		tree.setShowsRootHandles(true);

		JScrollPane scrollPane = new JScrollPane(tree);
		add(scrollPane);
	}

	/** Remove all nodes except the root node. */
	public void clear () {
		ArrayList<TreeNode> allChildren = collectNodes(getCurrentNode());
		ArrayList<TreeNode> removalQueue = new ArrayList<>();
		for (TreeNode child : allChildren) {
			if (!protectedNodes.contains(child)) {
				removalQueue.add(child);
			}
		}
		for (TreeNode node : removalQueue) {
			model.removeNodeFromParent((MutableTreeNode) node);
		}
		model.reload();
	}

	private ArrayList<TreeNode> collectNodes () {
		return new ArrayList<>(collectNodes(rootNode));
	}

	private ArrayList<TreeNode> collectNodes (TreeNode node) {
		ArrayList<TreeNode> result = new ArrayList<>();
		result.add(node);
		for (TreeNode child : Collections.list(node.children())) {
			result.addAll(collectNodes(child));
		}
		return result;
	}

	public DefaultMutableTreeNode getCurrentNode () {
		TreePath currentSelection = tree.getSelectionPath();
		return (DefaultMutableTreeNode) currentSelection.getLastPathComponent();
	}

	/**
	 * Remove currently selected node if it is not protected.
	 */
	public void removeCurrentNode () {
		boolean finished = false;
		TreePath currentSelection = tree.getSelectionPath();
		if (currentSelection != null) {
			DefaultMutableTreeNode currentNode = (DefaultMutableTreeNode) currentSelection.getLastPathComponent();
			if (!protectedNodes.contains(currentNode)) {
				MutableTreeNode parent = (MutableTreeNode) currentNode.getParent();
				if (parent != null) {
					model.removeNodeFromParent(currentNode);
					finished = true;
				}
			}
		}
		if (!finished) {// Either there was no selection, or the root was selected.
			toolkit.beep();
		}
	}

	public boolean protectNode (TreeNode node) {
		return !protectedNodes.add(node) && node.getParent() != null && protectNode(node.getParent());
	}

	/** Add child to the currently selected node. */
	public DefaultMutableTreeNode addObject (Object child) {
		DefaultMutableTreeNode parentNode;
		TreePath parentPath = tree.getSelectionPath();

		if (parentPath == null) {
			parentNode = rootNode;
		} else {
			parentNode = (DefaultMutableTreeNode) parentPath.getLastPathComponent();
		}

		return addObject(parentNode, child, true);
	}

	public DefaultMutableTreeNode addObject (DefaultMutableTreeNode parent, Object child) {
		return addObject(parent, child, false);
	}

	public DefaultMutableTreeNode addObject (DefaultMutableTreeNode parent, Object child, boolean shouldBeVisible) {
		DefaultMutableTreeNode childNode = new DefaultMutableTreeNode(child);

		if (parent == null) {
			parent = rootNode;
		}

		//It is key to invoke this on the TreeModel, and NOT DefaultMutableTreeNode
		model.insertNodeInto(childNode, parent, parent.getChildCount());

		//Make sure the user can see the lovely new node.
		if (shouldBeVisible) {
			tree.scrollPathToVisible(new TreePath(childNode.getPath()));
		}
		return childNode;
	}

	static class MyTreeModelListener implements TreeModelListener {
		public void treeNodesChanged (TreeModelEvent e) {
			DefaultMutableTreeNode node;
			node = (DefaultMutableTreeNode) (e.getTreePath().getLastPathComponent());

			/*
			 * If the event lists children, then the changed
			 * node is the child of the node we've already
			 * gotten.  Otherwise, the changed node and the
			 * specified node are the same.
			 */

			int index = e.getChildIndices()[0];
			node = (DefaultMutableTreeNode) (node.getChildAt(index));

			LogManager.getRootLogger().info("The user has finished editing the node.");
			LogManager.getRootLogger().info("New value: " + node.getUserObject());
		}

		public void treeNodesInserted (TreeModelEvent e) {
		}

		public void treeNodesRemoved (TreeModelEvent e) {
		}

		public void treeStructureChanged (TreeModelEvent e) {
		}

	}

}
