import wx
import icons
import imagepanel
import wx.lib.agw.aui.auibar


class UI:
    def __init__(self, app):
        self.app = app

        self.toolbar = None
        self.capture_tool = None
        self.upload_tool = None
        self.edit_tool = None
        self.save_tool = None
        self.help_tool = None
        self.help_menu = None

        self.image_panel = imagepanel.ImagePanel(self.app)
        self.create_toolbar()
        self.fill_main_toolbar()

        self.app.subscribe("uploading", self.upload_event)
        self.app.subscribe("screen_shot", self.screen_shot_changed)

    def set_screen_shot(self, image):
        self.image_panel.set_bitmap(image)

    def create_toolbar(self):
        self.toolbar = self.app.CreateToolBar(wx.TB_HORZ_TEXT | wx.TB_HORZ_LAYOUT | wx.BORDER)
        self.toolbar.SetToolBitmapSize((24, 24))

    def fill_main_toolbar(self):
        enabled = not self.app.uploading and self.app.screen_shot is not None

        self.toolbar.ClearTools()

        self.capture_tool = self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key, True)
        self.save_tool = self.add_tool("Save", icons.SAVE, self.on_save, enabled)
        self.edit_tool = self.add_tool("Edit", icons.PENCIL, self.on_edit, enabled)
        self.upload_tool = self.add_tool("Upload", icons.UPLOAD, self.on_upload, enabled)
        self.add_tool("Settings", icons.SETTINGS, self.on_settings, True)
        self.help_tool = self.add_tool("Help", icons.INFO, self.on_help, True)

        self.create_help_menu()

        self.toolbar.Realize()

    def fill_edit_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool()
        self.add_tool("Color", icons.RECTANGLE_FILLED, self.on_select_color, True)
        self.add_tool("Pencil", icons.PENCIL, self.on_back, True)
        self.add_tool("Brush", icons.BRUSH, self.on_back, True)
        self.add_tool("Shapes", icons.RECTANGLE, self.on_back, True)
        self.add_tool("Eraser", icons.CANCEL, self.on_back, True)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback, enabled=False):
        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)

        self.toolbar.EnableTool(tool.GetId(), enabled)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def add_back_tool(self, callback=None):
        if callback is None:
            callback = self.on_back

        self.add_tool("Back", icons.BACK, callback, True)

    def create_help_menu(self):
        self.help_menu = wx.Menu()

        UI.create_menu_item(self.help_menu, "TEST", None)

    @staticmethod
    def create_menu_item(menu, label, func):
        item = wx.MenuItem(menu, -1, label)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def upload_event(self, old_value, uploading):
        self.toolbar.EnableTool(self.upload_tool.GetId(), not uploading)
        self.toolbar.EnableTool(self.capture_tool.GetId(), not uploading)
        self.toolbar.EnableTool(self.edit_tool.GetId(), not uploading)

    def screen_shot_changed(self, old, new):
        self.toolbar.EnableTool(self.upload_tool.GetId(), True)
        self.toolbar.EnableTool(self.save_tool.GetId(), True)
        self.toolbar.EnableTool(self.edit_tool.GetId(), True)

    def on_back(self, event):
        self.fill_main_toolbar()

    def on_upload(self, event):
        self.app.send()

    def on_save(self, event):
        save_dialog = wx.FileDialog(self.app, "Save PNG file", "", "",
                                    "PNG files (*.png)|*.png", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if save_dialog.ShowModal() == wx.ID_CANCEL:
            return

        self.app.save(save_dialog.GetPath())

    def on_settings(self, event):
        pass

    def on_edit(self, event):
        self.fill_edit_toolbar()

    def on_help(self, event):
        bar_pos = self.toolbar.GetScreenPosition()-self.app.GetScreenPosition()

        # This is the position of the tool along the tool bar (1st, 2nd, 3rd, etc...)
        tool_index = self.toolbar.GetToolPos(event.GetId())

        # Get the size of the tool
        tool_size = self.toolbar.GetToolSize()

        # This is the upper left corner of the clicked tool
        upper_left_pos = (bar_pos[0]+tool_size[0]*tool_index, bar_pos[1])

        # Menu position will be in the lower right corner
        lower_right_pos = (bar_pos[0]+tool_size[0]*(tool_index+1), bar_pos[1]+tool_size[1])

        #origin = self.help_tool.GetControl().GetPosition()
        self.app.PopupMenuXY(self.help_menu, *upper_left_pos)

    def on_select_color(self, event):
        data = wx.ColourData()
        data.SetColour(wx.Colour(255, 0, 0))
        data.SetChooseFull(True)

        color_dialog = wx.ColourDialog(self.app, data)

        if color_dialog.ShowModal() == wx.ID_CANCEL:
            return