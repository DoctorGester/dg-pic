import wx
import icons
import imagepanel


class UI:
    def __init__(self, app):
        self.app = app

        self.top_toolbar = None
        self.bot_toolbar = None
        self.capture_tool = None
        self.upload_tool = None

        self.image_panel = imagepanel.ImagePanel(self.app)
        self.create_top_toolbar()

    def set_screen_shot(self, image):
        self.image_panel.set_bitmap(image)

    def create_top_toolbar(self):
        self.top_toolbar = self.app.CreateToolBar(wx.TB_HORZ_TEXT | wx.TB_HORZ_LAYOUT | wx.BORDER)
        self.top_toolbar.SetToolBitmapSize((24, 24))

        self.capture_tool = self.add_tool("Capture", icons.PHOTO, self.app.on_capture_key)
        self.upload_tool = self.add_tool("Upload", icons.UPLOAD, self.on_upload)

        #self.toolbar.EnableTool(self.upload_tool.GetId(), False)

        self.top_toolbar.Realize()

    def add_tool(self, label, icon, callback):
        tool = self.top_toolbar.AddLabelTool(wx.ID_ANY, label=label, bitmap=icons.icon(icon), shortHelp=label)
        self.app.Bind(wx.EVT_MENU, callback, tool)

        return tool

    def on_upload(self, event):
        self.app.send()