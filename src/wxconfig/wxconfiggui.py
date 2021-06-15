import wx
import logging
from wxconfig import Config


class SettingsDialog(wx.Dialog):
    """
    A dialog box for changing settings. A tab for each root node, with a tree view on left for every branch and a text
    box for every value.
    """

    # Settings
    __settings = None  # Will set in init.

    # Store any settings that have changed
    changed_settings = {}

    def __init__(self, parent, exclude=None):
        """
        Open the settings dialog
        :param parent: The parent frame for this dialog
        :param exclude: List of settings root nodes to exclude from this dialog
        """

        # Super Constructor
        wx.Dialog.__init__(self, parent=parent, id=wx.ID_ANY, title="Settings",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # Get the dialog size, position and style from settings if set
        x = Config().get('settings_window.x')
        y = Config().get('settings_window.y')
        width = Config().get('settings_window.width')
        height = Config().get('settings_window.height')
        style = Config().get('settings_window.style')

        # Set point and size if both variables are available in config, else None
        point = None if x is None or y is None else wx.Point(x=x, y=y)
        size = None if width is None or height is None else wx.Size(width=width, height=height)

        if point is not None:
            self.SetPosition(point)
        if size is not None:
            self.SetSize(size)

        # Override style if it is available in config. Default has already been set as
        # wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BOARDER
        if style is not None:
            self.SetWindowStyle(style)

        self.SetTitle("Settings")

        # Create logger and get config
        self.__log = logging.getLogger(__name__)
        self.__settings = Config()

        # Dict of changes. Will commit only on ok
        self.__changes = {}

        # Settings to exclude. Just settings_window if None. Add settings_window if not specified.
        exclude = ['settings_window'] if exclude is None else exclude
        if 'settings_window' not in exclude:
            exclude.append('settings_window')

        # We want 2 vertical sections, the tabbed notebook and the buttons. The buttons sizer will have 2 horizontal
        # sections, one for each button.
        main_sizer = wx.BoxSizer(wx.VERTICAL)  # Notebook panel
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)  # Button sizer

        # Notebook
        self.__notebook = wx.Notebook(self, wx.ID_ANY)  # The notebook

        # A tab for each root node in config. We will store the tabs components in lists which can be accessed by the
        # index returned from notebook.GetSelectedItem()
        root_nodes = self.__settings.get_root_nodes()
        self.__tabs = []
        for node in root_nodes:
            # Exclude?
            if node not in exclude:
                # Create new tab
                self.__tabs.append(SettingsTab(self, self.__notebook, node))

                # Add tab to notebook
                self.__notebook.AddPage(self.__tabs[-1], node)

        # Buttons
        button_ok = wx.Button(self, label="Update")
        button_cancel = wx.Button(self, label="Cancel")
        button_sizer.Add(button_ok, 0, wx.ALL, 1)
        button_sizer.Add(button_cancel, 0, wx.ALL, 1)

        # Add notebook and button sizer to main sizer and set main sizer for window
        main_sizer.Add(self.__notebook, 1, wx.ALL | wx.EXPAND, 5)
        main_sizer.Add(button_sizer)
        self.SetSizer(main_sizer)

        # Bind buttons & notebook page select.
        button_ok.Bind(wx.EVT_BUTTON, self.__on_ok)
        button_cancel.Bind(wx.EVT_BUTTON, self.__on_cancel)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.__on_page_select)

        # Bind window close event
        self.Bind(wx.EVT_CLOSE, self.__on_close, self)

        # Call on_page_select to select the first page
        self.__on_page_select(event=None)

    def __on_page_select(self, event):
        # Call the tabs select method to populate
        index = self.__notebook.GetSelection()
        self.__tabs[index].select()

    def __on_cancel(self, event):
        # Clear changed settings and close
        self.changed_settings = {}
        self.EndModal(wx.ID_CANCEL)
        self.Close()

    def __on_ok(self, event):
        # Update settings and save
        delkeys = []
        for setting in self.changed_settings:
            # Get the current and new setting
            orig_value = self.__settings.get(setting)
            new_value = self.changed_settings[setting]

            # We need to retain data type. New values will all be string as they were retrieved from textctl.
            # Get the data type of the original and cast new to it. Note boolean needs to be handled differently as it
            # doesn't cast directly.
            if isinstance(orig_value, bool):
                new_value = new_value.lower() in ['true', '1', 'yes', 't']
            else:
                new_value = type(orig_value)(new_value)

            # If they are the same, discard from changes. We will use a list of items to delete (delkeys) as we cant
            # delete whilst iterating. If they are different, update settings.
            if orig_value == new_value:
                delkeys.append(setting)
            else:
                self.__settings.set(setting, new_value)

        # Now delete the items that were the same from changed_settings. changed_settings may be used by settings
        # dialog caller.
        for key in delkeys:
            del(self.changed_settings[key])

        # Save the settings and close dialog
        self.__settings.save()
        self.EndModal(wx.ID_OK)
        self.Close()

    def __on_close(self, event):
        # Save pos and size
        x, y = self.GetPosition()
        width, height = self.GetSize()
        self.__settings.set('settings_window.x', x)
        self.__settings.set('settings_window.y', y)
        self.__settings.set('settings_window.width', width)
        self.__settings.set('settings_window.height', height)

        # Style
        style = self.GetWindowStyle()
        self.__settings.set('settings_window.style', style)

        # Save
        self.__settings.save()

        # Destroy
        self.Destroy()


class SettingsTab(wx.Panel):
    """
    A notebook tab containing the settings tree and values for a settings root node.
    """

    # Root node for this tab
    __root_node_name = None

    # Parent frame. Set during constructor
    __parent_frame = None

    # Each tab has: a tree view; a values panel; and a list of value text boxes bound to a change
    # event.
    __tree = None
    __tab_sizer = None

    # Currently displayed value panel. Will be switched when tree menu items are selected.
    __current_value_panel = None

    def __init__(self, parent_frame, notebook, root_node):
        """
        Creates a tab for the settings notebook.

        :param parent_frame: The frame containing the notebook.
        :param notebook. The notebook that this tab should be part of.
        :param root_node. The root node name for the settings
        """
        # Super Constructor
        wx.Panel.__init__(self, parent=notebook)

        # Store the parent frame and get the settings for this tab.
        self.__parent_frame = parent_frame

        # Store the root node for this tab
        self.__root_node_name = root_node

        # Create logger
        self.__log = logging.getLogger(__name__)

        # Build the tab and set it's sizer.
        self.__tab_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.__tab_sizer)

        # Create tree control and add it to sizer
        self.__tree = SettingsTree(self, self.__root_node_name)
        self.__tab_sizer.Add(self.__tree, 1, wx.ALL | wx.EXPAND, 1)

        # Bind tree selection changed
        self.__tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.__on_tree_select)

    def select(self):
        """
        To be called when this tab is selected. Populate value sizer for the selected item, If no item is selected,
        populate for root.
        :return:
        """
        selected_item = self.__tree.GetSelection()
        if selected_item.ID is None:
            root_node = self.__tree.GetRootItem()
            setting_path = self.__tree.GetItemData(root_node)
        else:
            setting_path = self.__tree.GetItemData(selected_item)

        # Set the panel
        self.__switch_value_panel(setting_path)

    def __on_tree_select(self, event):
        """
        Called when an item in the tree is selected. Displays the correct settings panel
        :param event:
        :return:
        """
        # Get Selected item and check that it is a tree item
        tree_item = event.GetItem()
        if not tree_item.IsOk():
            return

        # Get the setting path from item data
        setting_path = self.__tree.GetItemData(tree_item)

        # Switch the panel
        self.__switch_value_panel(setting_path)

    def __switch_value_panel(self, setting_path):
        """
        Switched the value panel to the correct one for the settings path
        :param setting_path:
        :return:
        """
        # Get current panel and delete.
        if self.__current_value_panel is not None:
            self.__current_value_panel.Destroy()

        # Create the new value panel and add to sizer.
        self.__current_value_panel = SettingsValuePanel(self.__parent_frame, self, setting_path)
        self.__tab_sizer.Add(self.__current_value_panel, 1, wx.ALL | wx.EXPAND, 1)

        # Redraw
        self.__tab_sizer.Layout()


class SettingsTree(wx.TreeCtrl):
    """
    A Tree control containing the settings nodes settings node
    """

    __root_node_name = None
    __helptext = {}

    def __init__(self, settings_tab, settings_node):
        """
        Creates a tree control for specified settings node.

        :param settings_tab. The settings_tab on which this tree control should be displayed.
        :param settings_node. The node name for the settings who's values will be presented
        """
        # Super Constructor
        wx.TreeCtrl.__init__(self, parent=settings_tab)

        # Set root node
        self.__root_node_name = settings_node

        # Build the tree. Bind the
        self.__build_tree(None, self.__root_node_name)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.__display_tooltip)

        # Set max size. Width should be best size width, height should be auto (-1)
        best_width = self.GetBestSize()[0] * 2  # Hack, best size not working
        self.SetMaxSize((best_width, -1))

    def __build_tree(self, node, node_name):
        """
        Recursive function to build the tree and value panels from the node using the settings
        :param node: The tree view node to build from. If none, builds from root.
        :param node_name. The name of the node to build from.
        """

        # Build root node if node is None
        if node is None:
            node = self.AddRoot(self.__root_node_name)
            self.SetItemData(node, self.__root_node_name)

        # Get settings
        node_path = self.GetItemData(node)
        settings = Config().get(node_path)

        # Iterate settings, adding branches. Recurse to add sub branches.
        for setting in settings:
            # Get settings path
            settings_path = f"{self.GetItemData(node)}.{setting}"

            # Get value. If dict, add the node and recursively call this function again.
            value = settings[setting]
            if type(value) is dict:
                # Get metadata for branch if available
                branch_name = Config().get_meta(settings_path, '__label')
                branch_helptext = Config().get_meta(settings_path, '__helptext')

                # Add the node and set its settings path
                node_id = self.AppendItem(node, setting if branch_name is None else branch_name)
                self.SetItemData(node_id, settings_path)

                # If there is helptext for the branch, store it against node_id. We will use it in get tool tip event
                # handler.
                if branch_helptext is not None:
                    self.__helptext[node_id] = branch_helptext

                # Recurse
                self.__build_tree(node_id, value)

    def __display_tooltip(self, event):
        """
        Displays sets teh tooltip for the tree item
        :return:
        """
        item = event.GetItem()

        if item in self.__helptext:
            helptext = self.__helptext[item]
            event.SetToolTip(helptext)


class SettingsValuePanel(wx.ScrolledWindow):
    """
    A panel containing text boxes for editing values for a settings node
    """

    __value_sizer = None
    __value_boxes = []

    def __init__(self, parent_frame, settings_tab, node):
        """
        Creates a panel containing values for a settings node.

        :param parent_frame: The frame containing the notebook.
        :param settings_tab. The settings_tab on which this panel should be displayed.
        :param node. The node name for the settings who's values will be presented
        """
        # Super Constructor
        wx.ScrolledWindow.__init__(self, parent=settings_tab)

        # Create logger
        self.__log = logging.getLogger(__name__)

        # Store the parent frame and get the settings for this node.
        self.__parent_frame = parent_frame
        self.__settings = Config().get(node)

        leaf_settings = {}
        for setting in self.__settings:
            if type(self.__settings[setting]) is not dict:
                leaf_settings[setting] = self.__settings[setting]

        # Add the value sizer for settings values.
        self.__value_sizer = wx.FlexGridSizer(rows=len(leaf_settings), cols=2, vgap=2, hgap=2)

        # Add the sizer to the panel
        self.SetSizer(self.__value_sizer)

        # Display every value
        for setting in leaf_settings:
            # Setting path
            setting_path = f"{node}.{setting}"

            # Value. Make sure that we display changed value if already changed
            if setting_path in self.__parent_frame.changed_settings:
                value = self.__parent_frame.changed_settings[setting_path]
            else:
                value = leaf_settings[setting]

            # Create the label. If we have a label defined in metadata, use it, else use the setting.
            label_text = Config().get_meta(setting_path, '__label')
            label_text = setting if label_text is None else label_text
            label = wx.StaticText(self, wx.ID_ANY, label_text, style=wx.ALIGN_LEFT)

            # Create the value box. If we have a helptext defined in metadata, set as tooltip.
            help_text = Config().get_meta(setting_path, '__helptext')
            self.__value_boxes.append(wx.TextCtrl(self, wx.ID_ANY, f"{value}", style=wx.ALIGN_LEFT))
            if help_text is not None:
                self.__value_boxes[-1].SetToolTip(help_text)

            # Add label and value to value sizer
            self.__value_sizer.AddMany([(label, 0, wx.EXPAND), (self.__value_boxes[-1], 0, wx.EXPAND)])

            # Bind to text change. We need to generate a handler as this will have a parameter.
            self.__value_boxes[-1].Bind(wx.EVT_TEXT, self.__get_on_change_evt_handler(setting_path=setting_path))

        # Layout the value sizer
        self.__value_sizer.Layout()

        # Setup scrollbars
        self.SetScrollbars(1, 1, 1000, 1000)

    def __get_on_change_evt_handler(self, setting_path):
        """
        Returns a new event handler with a parameter of the settings path
        :param setting_path:
        :return:
        """

        def on_value_changed(event):
            old_val = self.__settings.get(setting_path)
            self.__parent_frame.changed_settings[setting_path] = event.String
            self.__log.debug(f"Value changed from {old_val} to {self.__parent_frame.changed_settings[setting_path]} "
                             f"for {setting_path}.")

        return on_value_changed


if __name__ == '__main__':
    """
    Displays the wxconfig dialog using the text config files. Useful for testing the GUI.
    """
    import definitions

    # Load the config
    Config().load(fr"{definitions.TEST_DIR}\testconfig.yaml",
                      meta=fr"{definitions.TEST_DIR}\testconfigmeta.yaml")

    # Create the app and frame
    app = wx.App(False)
    frame = wx.Frame()
    frame.Show()
    app.MainLoop()

    # Display the dialog
    settings_dialog = SettingsDialog(parent=None, exclude=[])
    res = settings_dialog.ShowModal()

