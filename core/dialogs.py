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

    def bind_shortcut(self, name, parameter, method):
        label = wx.StaticText(self.panel, label=name)
        text = wx.TextCtrl(self.panel)

        def on_key_press(event):
            key_string = SettingsDialog.get_pressed_key_string(event)
            text.SetValue(key_string)
            self.app.config.set(parameter, key_string)
            method(key_string)

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

        self.bind_shortcut("Capture", "capture_shortcut", self.app.register_capture_key)
        self.bind_shortcut("Instant full screen", "instant_screen_shortcut", self.app.register_instant_screen_key)

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

        # self.bind_text_config_parameter("Save uploaded images to", "gallery_dir")

        h_box.Add(self.sizer, proportion=1, flag=wx.ALL | wx.EXPAND, border=15)
        self.panel.SetSizer(h_box)

        self.panel.Fit()
        self.Fit()

    key_map = {}

    @staticmethod
    def gen_key_map():
        keys = ("BACK", "TAB", "RETURN", "ESCAPE", "SPACE", "DELETE", "START",
                "LBUTTON", "RBUTTON", "CANCEL", "MBUTTON", "CLEAR", "PAUSE",
                "CAPITAL", "PRIOR", "NEXT", "END", "HOME", "LEFT", "UP", "RIGHT",
                "DOWN", "SELECT", "PRINT", "EXECUTE", "SNAPSHOT", "INSERT", "HELP",
                "NUMPAD0", "NUMPAD1", "NUMPAD2", "NUMPAD3", "NUMPAD4", "NUMPAD5",
                "NUMPAD6", "NUMPAD7", "NUMPAD8", "NUMPAD9", "MULTIPLY", "ADD",
                "SEPARATOR", "SUBTRACT", "DECIMAL", "DIVIDE", "F1", "F2", "F3", "F4",
                "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13", "F14",
                "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24",
                "NUMLOCK", "SCROLL", "PAGEUP", "PAGEDOWN", "NUMPAD_SPACE",
                "NUMPAD_TAB", "NUMPAD_ENTER", "NUMPAD_F1", "NUMPAD_F2", "NUMPAD_F3",
                "NUMPAD_F4", "NUMPAD_HOME", "NUMPAD_LEFT", "NUMPAD_UP",
                "NUMPAD_RIGHT", "NUMPAD_DOWN", "NUMPAD_PRIOR", "NUMPAD_PAGEUP",
                "NUMPAD_NEXT", "NUMPAD_PAGEDOWN", "NUMPAD_END", "NUMPAD_BEGIN",
                "NUMPAD_INSERT", "NUMPAD_DELETE", "NUMPAD_EQUAL", "NUMPAD_MULTIPLY",
                "NUMPAD_ADD", "NUMPAD_SEPARATOR", "NUMPAD_SUBTRACT", "NUMPAD_DECIMAL",
                "NUMPAD_DIVIDE")

        for i in keys:
            SettingsDialog.key_map[getattr(wx, "WXK_"+i)] = i
        for i in ("SHIFT", "ALT", "CONTROL", "MENU"):
            SettingsDialog.key_map[getattr(wx, "WXK_"+i)] = ''

    @staticmethod
    def get_pressed_key_string(event):
        key_code = event.GetKeyCode()
        key_name = SettingsDialog.key_map.get(key_code, None)
        modifiers = ""
        for mod, ch in ((event.ControlDown(), 'control-'),
                        (event.AltDown(),     'alt-'),
                        (event.ShiftDown(),   'shift-'),
                        (event.MetaDown(),    'meta-')):
            if mod:
                modifiers += ch

        if key_name is None:
            if 27 < key_code < 256:
                key_name = chr(key_code)
            else:
                key_name = "(%s)unknown" % key_code

        if len(key_name) is 0:
            return modifiers[:len(modifiers) - 1]
        else:
            return modifiers + key_name

SettingsDialog.gen_key_map()


class GalleryDialog(wx.Dialog):

    def __init__(self, app, title, go_to_gallery_handler, content_provider):
        super(GalleryDialog, self).__init__(parent=app, title=title)

        self.app = app
        self.go_to_gallery_handler = go_to_gallery_handler
        self.content_provider = content_provider

    def ShowModal(*args, **kwargs):
        self = args[0]
        super(GalleryDialog, self).ShowModal(args, kwargs)
        self.content_provider.get_names(self.on_names_loaded)

    def on_names_loaded(self, names):
        pass


class SimpleGalleryContentProvider:

    def __init__(self, names):
        self.names = names

    def get_names(self, callback):
        callback(self.names)