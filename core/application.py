import wx
import win32con
import io
import capture
import traycontrol
import webbrowser
import config
import json
import clipboard
import storage
import upload
import ui


class AppFrame(wx.Frame):
    SITE_URL = "http://dg-pic.tk"

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
        self.combined_bitmap = None
        self.last_uploaded_url = None
        self.tray_control = traycontrol.TrayIcon(self)
        self.ui = ui.UI(self)

        self.register_capture_key(self.config.capture_shortcut)

        if self.config.instant_screen_shortcut is not None:
            self.register_instant_screen_key(self.config.instant_screen_shortcut)

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

    def register_capture_key(self, key):
        self.register_global_key(key, "alt-shift-s", 0, self.on_capture_key)

    def register_instant_screen_key(self, key):
        self.register_global_key(key, "control-shift-d", 1, self.on_full_screen_key)

    def register_global_key(self, key, default, bind_id, callback):
        self.UnregisterHotKey(bind_id)
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
        self.last_uploaded_url = None
        self.ui.bottom_bar_show_progress()

        if self.combined_bitmap:
            self.combined_bitmap.Destroy()

        self.combined_bitmap = self.ui.image_panel.get_combined_bitmap()
        image = self.combined_bitmap.ConvertToImage()
        stream = io.BytesIO()
        image.SaveStream(stream, wx.BITMAP_TYPE_PNG)

        files = {
            "image": ("captured.png", stream.getvalue())
        }

        if self.config.show_balloons:
            self.tray_control.show_info("Upload has started")

        self.uploading = True
        upload.upload_file(self, self.config.upload_url, files)

    def on_upload_progress(self, event):
        self.ui.set_upload_progress(int(event.uploaded / event.total * 100))

    def on_upload_finished(self, event):
        parsed = json.loads(event.text())

        if parsed["success"] is False:
            if self.config.show_balloons:
                self.tray_control.show_error("Upload error: " + parsed["message"])

            self.ui.bottom_bar_show_text("Error: " + parsed["message"])

            print parsed["message"]
        else:
            self.last_uploaded_url = parsed["answer"]["url"]
            full_url = self.config.basic_url.format(self.last_uploaded_url)
            self.ui.bottom_bar_show_link(full_url)

            if self.config.store_images_locally:
                storage.store_image(self.config, self.last_uploaded_url, self.combined_bitmap)
                storage.store_thumbnail(self.config.mini_url, self.last_uploaded_url)

            if self.config.put_url_into_clipboard:
                clipboard.set_data(full_url)

                if self.config.show_balloons:
                    self.tray_control.show_info("Uploaded to: " + full_url)

            if self.config.open_in_browser_after_upload:
                self.go_to_image_link()

            if self.config.store_local_history:
                history = self.config.history

                if not history:
                    history = []

                history.append(self.last_uploaded_url)
                self.config.history = history

        self.uploading = False

    def go_to_image_link(self):
        AppFrame.go_to_link(self.config.basic_url.format(self.last_uploaded_url))

    def save(self, path):
        combined = self.ui.image_panel.get_combined_bitmap()
        combined.ConvertToImage().SaveFile(path, wx.BITMAP_TYPE_PNG)
        combined.Destroy()

    def screen_shot_from_selection(self, selection):
        bitmap = wx.EmptyBitmap(selection.width, selection.height)

        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, selection.width, selection.height, wx.MemoryDC(self.full_screen), selection.x, selection.y)
        memory.SelectObject(wx.NullBitmap)

        return bitmap

    def set_screen_shot(self, screen_shot):
        w = screen_shot.GetWidth()
        h = screen_shot.GetHeight()

        if w == 0 and h == 0:
            return

        if self.screen_shot:
            self.screen_shot.Destroy()

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

            if self.config.move_window_at_capture:
                self.move_with_canvas_offset(combined.x, combined.y)

    def on_motion(self, display, event):
        if self.in_capture():
            self.selection_end = AppFrame.get_display_relative_event_point(display, event)

            for frame in self.capture_frames:
                frame.should_redraw = True

    def on_capture_key(self, evt):
        if self.ui.are_settings_open():
            return

        if not self.in_capture():
            self.full_screen = self.get_full_screen()
            amount = range(wx.Display.GetCount())
            self.capture_frames = [capture.CaptureFrame(self, wx.Display(i), self.full_screen) for i in amount]
        else:
            if self.config.double_press_captures_full_screen:
                self.set_screen_shot(self.full_screen)

                if self.config.move_window_at_capture:
                    self.move_with_canvas_offset(0, 0)

            self.close_capture_frames()

    def on_full_screen_key(self, evt):
        if self.ui.are_settings_open():
            return

        if not self.in_capture():
            self.full_screen = self.get_full_screen()
            self.set_screen_shot(self.full_screen)

    def on_iconify(self, event):
        if self.IsIconized() and not self.config.minimize_on_close:  # This is dumb, but absolutely needed
            self.Hide()

    def move_with_canvas_offset(self, x, y):
        difference = (self.ui.image_panel.GetScreenPosition() - self.GetScreenPosition())

        self.MoveXY(max(0, x - difference.x), max(0, y - difference.y))

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
    def go_to_link(link):
        webbrowser.open_new_tab(link)

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