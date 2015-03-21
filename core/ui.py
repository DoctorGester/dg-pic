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
        self.color_tool = None
        self.edit_tool = None
        self.save_tool = None
        self.help_tool = None
        self.help_menu = None

        self.current_color = wx.Colour(255, 0, 0)

        self.image_panel = imagepanel.ImagePanel(self)
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

        self.capture_tool = self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key)
        self.save_tool = self.add_tool("Save", icons.SAVE, self.on_save, enabled)
        self.edit_tool = self.add_tool("Edit", icons.PENCIL, self.on_edit, enabled)
        self.upload_tool = self.add_tool("Upload", icons.UPLOAD, self.on_upload, enabled)
        self.add_tool("Settings", icons.SETTINGS, self.on_settings)
        self.help_tool = self.add_tool("Help", icons.INFO, self.on_help)

        self.toolbar.Realize()

    def fill_edit_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool()
        self.color_tool = self.add_tool("Color", icons.RECTANGLE_FILLED, self.on_select_color)
        self.add_tool("Pencil", icons.PENCIL, self.on_back)
        self.add_tool("Brush", icons.BRUSH, self.on_back)
        self.add_tool("Fill", icons.RECTANGLE_FILLED, self.on_back)
        self.add_tool("Shapes", icons.RECTANGLE, self.on_shapes)
        self.add_tool("Text", icons.TEXT, self.on_back)
        self.add_tool("Eraser", icons.CANCEL, self.on_back)

        self.toolbar.Realize()

        self.update_color_tool()

    def fill_help_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool()
        self.add_tool("Site", icons.INFO, self.on_back)
        self.add_tool("Feedback", icons.INFO, self.on_back)
        self.add_tool("Updates", icons.INFO, self.on_back)
        self.add_tool("About", icons.INFO, self.on_back)

        self.toolbar.Realize()

    def fill_shapes_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool(self.on_edit)
        self.add_tool("Line", icons.RECTANGLE, self.on_back)
        self.add_tool("Curve", icons.RECTANGLE, self.on_back)
        self.add_tool("Circle", icons.RECTANGLE, self.on_back)
        self.add_tool("Rectangle", icons.RECTANGLE, self.on_back)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback, enabled=True):
        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)

        self.toolbar.EnableTool(tool.GetId(), enabled)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def add_back_tool(self, callback=None):
        if callback is None:
            callback = self.on_back

        self.add_tool("Back", icons.BACK, callback, True)

    def update_color_tool(self):
        self.color_tool.SetNormalBitmap(icons.replace_color(icons.RECTANGLE_FILLED, self.current_color))
        self.toolbar.Realize()

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

    def on_shapes(self, event):
        self.fill_shapes_toolbar()

    def on_edit(self, event):
        self.fill_edit_toolbar()

    def on_help(self, event):
        self.fill_help_toolbar()

    def on_select_color(self, event):
        data = wx.ColourData()
        data.SetColour(wx.Colour(255, 0, 0))
        data.SetChooseFull(True)

        color_dialog = wx.ColourDialog(self.app, data)

        if color_dialog.ShowModal() == wx.ID_CANCEL:
            return

        data = color_dialog.GetColourData()
        self.current_color = data.GetColour()

        self.update_color_tool()