import wx

TRAY_TOOLTIP = "dg-pic"


class TrayIcon(wx.TaskBarIcon):

    def __init__(self, app):
        super(TrayIcon, self).__init__()
        self.app = app
        self.set_icon("icon.ico")
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_show_app)

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    def show_info(self, text):
        self.ShowBalloon("Notification", text, flags=wx.ICON_INFORMATION)

    def show_error(self, text):
        self.ShowBalloon("Error", text, flags=wx.ICON_ERROR)

    # override
    def CreatePopupMenu(self):
        enabled = not self.app.uploading and self.app.screen_shot is not None
        menu = wx.Menu()
        TrayIcon.create_menu_item(menu, "Show App", self.on_show_app)
        TrayIcon.create_menu_item(menu, "Capture", self.on_capture, enabled)
        TrayIcon.create_menu_item(menu, "Upload", self.on_upload, enabled)
        menu.AppendSeparator()
        TrayIcon.create_menu_item(menu, "Exit", self.on_exit)
        return menu

    @staticmethod
    def create_menu_item(menu, label, func, enabled=True):
        item = wx.MenuItem(menu, -1, label)
        item.Enable(enabled)
        menu.Bind(wx.EVT_MENU, func, id=item.GetId())
        menu.AppendItem(item)
        return item

    def on_show_app(self, event):
        self.app.show()

    def on_capture(self, event):
        self.app.on_capture_key(event)

    def on_upload(self, event):
        self.app.send()

    def on_exit(self, event):
        self.app.on_close(event)