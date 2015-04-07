import wx
import tools
import icons
import dialogs
import imagepanel


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

        self.bottom_bar = None
        self.bottom_bar_sizer = None
        self.current_bottom_widget = None
        self.screen_shot_text = None
        self.screen_shot_link = None
        self.screen_shot_progress = None

        self.settings_dialog = None

        self.current_color = wx.Colour(255, 0, 0)
        self.brush_size = 4

        self.image_panel = None

        self.create_layout()
        self.create_toolbar()
        self.fill_main_toolbar()

        self.app.subscribe("uploading", self.upload_event)
        self.app.subscribe("screen_shot", self.screen_shot_changed)

    def are_settings_open(self):
        return self.settings_dialog is not None and self.settings_dialog.IsShown()

    def create_layout(self):
        top_level_panel = wx.Panel(self.app)

        self.image_panel = imagepanel.ImagePanel(top_level_panel, self)
        self.bottom_bar = wx.Panel(top_level_panel)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(self.image_panel, 1, wx.EXPAND | wx.ALL, 0)
        top_sizer.Add(self.bottom_bar, 0, wx.EXPAND | wx.ALL, 5)

        self.bottom_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.create_bottom_bar(self.bottom_bar, self.bottom_bar_sizer)

        self.bottom_bar.SetSizer(self.bottom_bar_sizer)

        top_level_panel.SetSizer(top_sizer)
        self.app.Layout()

    def create_bottom_bar(self, bar, sizer):
        self.screen_shot_text = wx.StaticText(bar, label="Press capture to get a shot")

        self.screen_shot_link = wx.HyperlinkCtrl(bar)
        self.screen_shot_link.Hide()

        self.screen_shot_progress = wx.Gauge(bar, style=wx.GA_HORIZONTAL | wx.GA_SMOOTH)
        self.screen_shot_progress.Hide()

        self.current_bottom_widget = self.screen_shot_text

        sizer.Add(self.screen_shot_text, 0, 5)
        sizer.Add((0, 0), 1, wx.EXPAND)
        sizer.Add(wx.Button(bar, label="Sign In"), 0, 5)
        sizer.Add(wx.Button(bar, label="Sign Up"))

        self.screen_shot_link.Bind(wx.EVT_HYPERLINK, self.on_link_clicked)

    def try_replace_bottom_widget(self, new):
        if self.current_bottom_widget is not new:
            self.current_bottom_widget.Hide()
            self.bottom_bar_sizer.Replace(self.current_bottom_widget, new)
            self.current_bottom_widget = new
            self.current_bottom_widget.Show()
            self.bottom_bar.Layout()

    def set_upload_progress(self, percent):
        self.screen_shot_progress.SetValue(percent)

    def bottom_bar_show_link(self, url):
        self.screen_shot_link.SetLabel(url)
        self.try_replace_bottom_widget(self.screen_shot_link)

    def bottom_bar_show_progress(self):
        self.try_replace_bottom_widget(self.screen_shot_progress)

    def bottom_bar_show_text(self, text):
        self.screen_shot_text.SetLabelText(text)
        self.try_replace_bottom_widget(self.screen_shot_text)

    def set_screen_shot(self, image):
        self.image_panel.set_bitmap(image)
        self.bottom_bar_show_text("Click upload to send your image")
        self.screen_shot_progress.SetValue(0)

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
        self.add_tool("Gallery", icons.LIST, self.on_gallery)
        self.add_tool("Settings", icons.SETTINGS, self.on_settings)
        self.help_tool = self.add_tool("Help", icons.INFO, self.on_help)

        self.toolbar.Realize()

        self.image_panel.set_tool(tools.WebImageTool())

    def fill_edit_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool()
        self.color_tool = self.add_tool("", icons.RECTANGLE_FILLED, self.on_select_color)
        self.add_draw_tool("Pencil", icons.PENCIL, tools.PencilTool())
        self.add_tool("Brush", icons.BRUSH, self.on_back)
        self.add_tool("Fill", icons.RECTANGLE_FILLED, self.on_back)
        self.add_tool("Shapes", icons.RECTANGLE, self.on_shapes)
        self.add_tool("Text", icons.TEXT, self.on_back)
        self.add_draw_tool("Eraser", icons.CANCEL, tools.EraserTool())

        self.toolbar.Realize()

        self.update_color_tool()
        self.image_panel.set_tool(tools.PencilTool())

    def fill_help_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool()
        self.add_tool("Site", icons.INFO, self.on_site_link)
        self.add_tool("Feedback", icons.INFO, self.on_back)
        self.add_tool("Updates", icons.INFO, self.on_back)
        self.add_tool("About", icons.INFO, self.on_about)

        self.toolbar.Realize()

    def fill_shapes_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool(self.on_edit)
        self.add_draw_tool("Line", icons.RECTANGLE, tools.LineTool())
        self.add_draw_tool("Ellipsis", icons.RECTANGLE, tools.EllipsisTool())
        self.add_draw_tool("Rectangle", icons.RECTANGLE, tools.RectangleTool())

        self.toolbar.Realize()

        self.image_panel.set_tool(tools.LineTool())

    def fill_gallery_toolbar(self):
        self.toolbar.ClearTools()

        self.add_back_tool(self.on_back)
        self.add_tool("Local", icons.RECTANGLE, self.on_back)
        self.add_tool("Online", icons.RECTANGLE, self.on_back)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback, enabled=True):
        bitmap = icons.icon(icon)

        # Debug
        if icon is not icons.BACK and callback == self.on_back:
            bitmap = icons.replace_color(icon, wx.Colour(190, 0, 0))

        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=bitmap, shortHelp=label)

        self.toolbar.EnableTool(tool.GetId(), enabled)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def add_draw_tool(self, label, icon, canvas_tool):
        bitmap = icons.icon(icon)
        tool = self.toolbar.AddRadioLabelTool(wx.ID_ANY, label=label, bitmap=bitmap, shortHelp=label)
        tool.SetClientData(canvas_tool)

        def on_draw_tool(event):
            self.image_panel.set_tool(canvas_tool)

        self.app.Bind(wx.EVT_MENU, on_draw_tool, tool)

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
        self.settings_dialog = dialogs.SettingsDialog(self.app)
        self.settings_dialog.ShowModal()

    def on_shapes(self, event):
        self.fill_shapes_toolbar()

    def on_edit(self, event):
        self.fill_edit_toolbar()

    def on_help(self, event):
        self.fill_help_toolbar()

    def on_gallery(self, event):
        self.fill_gallery_toolbar()

    def on_site_link(self, event):
        self.app.go_to_link(self.app.SITE_URL)

    def on_about(self, event):
        dialogs.AboutDialog(self.app)

    def on_select_color(self, event):
        data = wx.ColourData()
        data.SetColour(self.current_color)
        data.SetChooseFull(True)

        color_dialog = wx.ColourDialog(self.app, data)

        if color_dialog.ShowModal() == wx.ID_CANCEL:
            return

        data = color_dialog.GetColourData()
        self.current_color = data.GetColour()

        self.update_color_tool()

    def on_link_clicked(self, event):
        self.app.go_to_image_link()