import wx
import icons


class UI:
    def __init__(self, app):
        self.app = app

        self.toolbar = None
        self.create_toolbar()

    def create_toolbar(self):
        self.toolbar = self.app.CreateToolBar()
        self.toolbar.SetToolBitmapSize((24, 24))

        self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key)
        self.add_tool("Upload", icons.UPLOAD, self.on_upload)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback):
        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)
        self.app.Bind(wx.EVT_MENU, callback, tool)

    def on_upload(self, event):
        self.app.send()