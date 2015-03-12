import wx
import icons


class UI:
    def __init__(self, app):
        self.app = app

        self.toolbar = None
        self.capture_tool = None
        self.upload_tool = None

        self.create_toolbar()

    def create_toolbar(self):
        self.toolbar = self.app.CreateToolBar(wx.TB_HORZ_TEXT | wx.TB_HORZ_LAYOUT | wx.BORDER)
        self.toolbar.SetToolBitmapSize((24, 24))

        self.capture_tool = self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key)
        self.upload_tool = self.add_tool("Upload", icons.UPLOAD, self.on_upload)

        #self.toolbar.EnableTool(self.upload_tool.GetId(), False)

        self.toolbar.Realize()

    def add_tool(self, label, icon, callback):
        tool = self.toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def on_upload(self, event):
        self.app.send()