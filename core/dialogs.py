import wx


class AboutDialog():

    def __init__(self, parent):
        description = '''
                      dg-pic is an advanced screenshot tool
                      capable of taking pictures from multiple
                      screens, editing, saving and uploading
                      them to the web storage
                      '''

        info = wx.AboutDialogInfo()

        info.SetIcon(wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO))
        info.SetName("dg-pic")
        info.SetVersion("1.0")
        info.SetDescription(description)
        info.SetWebSite("http://dg-pic.tk")

        wx.AboutBox(info, parent)


class SettingsDialog(wx.Dialog):
    def __init__(self, app):
        super(SettingsDialog, self).__init__(parent=app, title="Settings")

        self.app = app
        self.sizer = None
        self.panel = None

        self.create_ui()

    def bind_bool_config_parameter(self, name, parameter):
        label = wx.StaticText(self.panel, label=name)
        box = wx.CheckBox(self.panel)

        def on_value_change(event):
            self.app.config.set(parameter, box.IsChecked())

        box.Bind(wx.EVT_CHECKBOX, on_value_change)
        box.SetValue(self.app.config.get(parameter))

        self.sizer.Add(label)
        self.sizer.Add((0, 0), 1)
        self.sizer.Add(box, flag=wx.ALIGN_RIGHT)

    def bind_shortcut_config_parameter(self, name, parameter):
        label = wx.StaticText(self.panel, label=name)
        text = wx.TextCtrl(self.panel)

        def append(original, value):
            if len(original) == 0:
                return value
            else:
                return original + "-" + value

        def on_key_press(event):
            key_code = event.GetKeyCode()
            value = ""

            if key_code > 256:
                return

            if event.ControlDown():
                value = append(value, "control")

            if event.AltDown():
                value = append(value, "alt")

            if event.ShiftDown():
                value = append(value, "shift")

            pressed_value = str(chr(key_code))
            text.SetValue(append(value, pressed_value))

        text.SetValue(self.app.config.get(parameter))
        text.Bind(wx.EVT_KEY_DOWN, on_key_press)

        self.sizer.Add(label)
        self.sizer.Add((0, 0), 1)
        self.sizer.Add(text)

    def create_ui(self):
        h_box = wx.BoxSizer(wx.HORIZONTAL)

        self.panel = wx.Panel(self)
        self.sizer = wx.FlexGridSizer(14, 3, 9, 25)
        self.sizer.AddGrowableCol(1, 1)

        self.bind_shortcut_config_parameter("Capture", "capture_shortcut")
        self.bind_shortcut_config_parameter("Instant full screen", "instant_screen_shortcut")

        self.bind_bool_config_parameter("Double shortcut captures full screen", "double_press_captures_full_screen")
        self.bind_bool_config_parameter("Minimize window on close", "minimize_on_close")
        self.bind_bool_config_parameter("Put image URL into clipboard", "put_url_into_clipboard")
        self.bind_bool_config_parameter("Resize window to fit an image", "resize_window_on_capture")
        self.bind_bool_config_parameter("Raise window after capture", "show_app_after_capture")
        self.bind_bool_config_parameter("Show tray balloons", "show_balloons")
        self.bind_bool_config_parameter("Start application minimized", "start_minimized")
        self.bind_bool_config_parameter("Store local upload history", "store_local_history")
        self.bind_bool_config_parameter("Store uploaded images locally", "store_images_locally")
        self.bind_bool_config_parameter("Upload immediately after capture", "upload_after_capture")
        self.bind_bool_config_parameter("Open image in browser after uploading", "open_in_browser_after_upload")
        self.bind_bool_config_parameter("Move window after capture", "move_window_at_capture")

        h_box.Add(self.sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(h_box)

        self.panel.Fit()
        self.Fit()