import wx
import win32con
import io
import capture
import traycontrol
import config
import json
import clipboard
import upload
import ui


class AppFrame(wx.Frame):
    UPLOAD_URL = "http://dg-pic.tk/upload?version=1"
    BASIC_URL = "http://dg-pic.tk/{0}"
    MINI_URL = "http://dg-pic.tk/{0}.mini"

    def __init__(self, application):
        wx.Frame.__init__(self, None, -1, "dg-pic")

        self.SetIcon(wx.Icon("icon.ico", wx.BITMAP_TYPE_ICO))

        self.observers = {}
        self.config = config.Config("config.json")

        self.app = application
        self.capture_frames = []
        self.in_selection = False
        self.uploading = False
        self.selection_start = (0, 0)
        self.selection_end = (0, 0)
        self.full_screen = None
        self.screen_shot = None
        self.last_uploaded_url = None
        self.tray_control = traycontrol.TrayIcon(self)
        self.ui = ui.UI(self)

        self.register_global_key(self.config.capture_shortcut, "alt-shift-s", 0, self.on_capture_key)

        if self.config.instant_screen_shortcut is not None:
            self.register_global_key(self.config.instant_screen_shortcut, "control-shift-d", 1, self.on_full_screen_key)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ICONIZE, self.on_iconify)
        self.Bind(upload.EVT_UPLOAD_FINISHED, self.on_upload_finished)
        self.Bind(upload.EVT_UPLOAD_PROGRESS, self.on_upload_progress)
        self.SetMinSize((600, 400))
        self.Center()
        self.Show()

        if self.config.start_minimized:
            self.Iconize(True)

    # For observer pattern
    def __setattr__(self, key, new_value):
        old_value = None

        if key in self.__dict__:
            old_value = self.__dict__[key]

        self.__dict__[key] = new_value

        if key in self.observers:
            for observer in self.observers[key]:
                observer(old_value, new_value)

    def subscribe(self, key, observer):
        if key not in self.observers:
            observer_list = []
            self.observers[key] = observer_list
        else:
            observer_list = self.observers[key]

        observer_list.append(observer)

    def register_global_key(self, key, default, bind_id, callback):
        print self.RegisterHotKey(bind_id, *self.parse_key(key, default))
        self.Bind(wx.EVT_HOTKEY, callback, id=bind_id)

    def parse_key(self, key, default):
        try:
            config_string = str(key.upper())
            words = str.split(config_string, "-")
            splitter = len(words) - 1
            mods = words[:splitter]
            key = words[splitter:][0]

            final_mod = 0

            for mod in mods:
                final_mod = final_mod | getattr(win32con, "MOD_" + mod)

            final_key = ord(key)

            if len(key) > 1 and hasattr(win32con, "VK_" + key):
                final_key = getattr(win32con, "VK_" + key)

            return final_mod, final_key
        except StandardError:
            return self.parse_key(default, default)

    def close_capture_frames(self):
        for frame in self.capture_frames:
            frame.Close()

        self.capture_frames = []

        if self.config.show_app_after_capture:
            self.show()

    def send(self):
        image = self.screen_shot.ConvertToImage()
        stream = io.BytesIO()
        image.SaveStream(stream, wx.BITMAP_TYPE_PNG)

        files = {
            "image": ("captured.png", stream.getvalue())
        }

        if self.config.show_balloons:
            self.tray_control.show_info("Upload has started")

        self.uploading = True
        upload.upload_file(self, AppFrame.UPLOAD_URL, files)

    def on_upload_progress(self, event):
        print("{0} / {1}".format(event.uploaded, event.total))

    def on_upload_finished(self, event):
        self.uploading = False

        parsed = json.loads(event.text())

        if parsed["success"] is False:
            if self.config.show_balloons:
                self.tray_control.show_error("Upload error: " + parsed["message"])

            print parsed["message"]
        else:
            self.last_uploaded_url = parsed["answer"]["url"]
            full_url = AppFrame.BASIC_URL.format(self.last_uploaded_url)

            if self.config.put_url_into_clipboard:
                clipboard.set_data(full_url)

                if self.config.show_balloons:
                    self.tray_control.show_info("Uploaded to: " + full_url)

            if self.config.store_local_history:
                history = self.config.history

                if not history:
                    history = []

                history.append(self.last_uploaded_url)
                self.config.history = history

    def save(self, path):
        self.screen_shot.ConvertToImage().SaveFile(path, wx.BITMAP_TYPE_PNG)

    def screen_shot_from_selection(self, selection):
        bitmap = wx.EmptyBitmap(selection.width, selection.height)

        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, selection.width, selection.height, wx.MemoryDC(self.full_screen), selection.x, selection.y)
        memory.SelectObject(wx.NullBitmap)

        return bitmap

    def set_screen_shot(self, screen_shot):
        self.screen_shot = screen_shot
        self.ui.set_screen_shot(screen_shot)
        self.Refresh()

        if self.config.resize_window_on_capture:
            difference = (self.ui.image_panel.GetBestVirtualSize() - self.screen_shot.GetSize())
            self.SetSize(self.GetSize() - difference)

        if self.config.upload_after_capture:
            wx.CallAfter(self.send)

    def get_selection_rect(self):
        x_min = min(self.selection_start[0], self.selection_end[0])
        x_max = max(self.selection_start[0], self.selection_end[0])
        y_min = min(self.selection_start[1], self.selection_end[1])
        y_max = max(self.selection_start[1], self.selection_end[1])

        top_left = wx.Point(x_min, y_min)
        bottom_right = wx.Point(x_max, y_max)

        return wx.Rect(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])

    def get_selection_for_display(self, display):
        geometry = display.GetGeometry()
        intersection = self.get_selection_rect().Intersect(geometry)

        return wx.Rect(intersection.x - geometry.x, intersection.y - geometry.y, intersection.width, intersection.height)

    def in_capture(self):
        return len(self.capture_frames) is not 0

    def on_left_down(self, display, event):
        if self.in_capture():
            self.in_selection = True
            self.selection_start = AppFrame.get_display_relative_event_point(display, event)

    def on_left_up(self, display, event):
        if self.in_capture():
            self.in_selection = False
            self.selection_end = AppFrame.get_display_relative_event_point(display, event)

            selection = self.get_selection_rect()

            selections = []
            for frame in self.capture_frames:
                copy = wx.Rect()
                copy.Set(*selection.Get())  # Somehow it doesn't work without copying the selection rect
                selections.append(copy.Intersect(frame.display.GetGeometry()))

            combined = AppFrame.combine_selections(selections)
            self.set_screen_shot(self.screen_shot_from_selection(combined))

            self.close_capture_frames()

    def on_motion(self, display, event):
        if self.in_capture():
            self.selection_end = AppFrame.get_display_relative_event_point(display, event)

            for frame in self.capture_frames:
                frame.should_redraw = True

    def on_capture_key(self, evt):
        if not self.in_capture():
            self.full_screen = self.get_full_screen()
            amount = range(wx.Display.GetCount())
            self.capture_frames = [capture.CaptureFrame(self, wx.Display(i), self.full_screen) for i in amount]
        else:
            if self.config.double_press_captures_full_screen:
                self.set_screen_shot(self.full_screen)

            self.close_capture_frames()

    def on_full_screen_key(self, evt):
        if not self.in_capture():
            self.full_screen = self.get_full_screen()
            self.set_screen_shot(self.full_screen)

    def on_iconify(self, event):
        if self.IsIconized() and not self.config.minimize_on_close:  # This is dumb, but absolutely needed
            self.Hide()

    def show(self):
        self.Show()
        self.Restore()
        self.Raise()
        self.SetFocus()

    def on_close(self, event):
        if self.config.minimize_on_close:
            self.Hide()
        else:
            self.Destroy()
            app.Exit()

    @staticmethod
    def get_full_screen():
        screen_dc = wx.ScreenDC()

        amount = range(wx.Display.GetCount())
        combined = AppFrame.combine_selections([wx.Display(i).GetGeometry() for i in amount])
        bitmap = wx.EmptyBitmap(combined.width, combined.height)

        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, combined.width, combined.height, screen_dc, 0, 0)
        memory.SelectObject(wx.NullBitmap)

        return bitmap

    @staticmethod
    def get_display_relative_event_point(display, event):
        display_start = display.GetGeometry().GetTopLeft().Get()
        return display_start[0] + event.GetX(), display_start[1] + event.GetY()

    @staticmethod
    def combine_selections(selections):
        result = wx.Rect()

        for selection in selections:
            result = result.Union(selection)

        return result

if __name__ == "__main__":
    app = wx.App()
    AppFrame(app)

    app.MainLoop()