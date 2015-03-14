import wx
import icons
import imagepanel


class UI:
    def __init__(self, app):
        self.app = app

        self.toolbar = None
        self.capture_tool = None
        self.upload_tool = None
        self.save_tool = None

        self.image_panel = imagepanel.ImagePanel(self.app)
        self.create_toolbar()

        self.app.subscribe("uploading", self.upload_event)
        self.app.subscribe("screen_shot", self.screen_shot_changed)

    def set_screen_shot(self, image):
        self.image_panel.set_bitmap(image)

    def create_toolbar(self):
        self.toolbar = self.app.CreateToolBar(wx.TB_HORZ_TEXT | wx.TB_HORZ_LAYOUT | wx.BORDER)
        self.toolbar.SetToolBitmapSize((24, 24))

        self.capture_tool = self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key)
        self.save_tool = self.add_tool("Save", icons.SAVE, self.on_save)
        self.upload_tool = self.add_tool("Upload", icons.UPLOAD, self.on_upload)

        self.toolbar.EnableTool(self.capture_tool.GetId(), True)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback):
        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)
        self.toolbar.EnableTool(tool.GetId(), False)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def upload_event(self, old_value, uploading):
        self.toolbar.EnableTool(self.upload_tool.GetId(), not uploading)
        self.toolbar.EnableTool(self.capture_tool.GetId(), not uploading)

    def screen_shot_changed(self, _, __):
        self.toolbar.EnableTool(self.upload_tool.GetId(), True)
        self.toolbar.EnableTool(self.save_tool.GetId(), True)

    def on_upload(self, event):
        self.app.send()

    def on_save(self, event):
        save_dialog = wx.FileDialog(self.app, "Save PNG file", "", "",
                                   "PNG files (*.png)|*.png", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if save_dialog.ShowModal() == wx.ID_CANCEL:
            return

        self.app.save(save_dialog.GetPath())