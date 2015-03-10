import wx
import win32con
import requests
import io
import capture
import imagepanel
import traycontrol

from config import Config


class AppFrame(wx.Frame):

    def __init__(self, application):
        wx.Frame.__init__(self, None, -1, "dg-pic")
        self.app = application
        self.capture_frames = []
        self.in_selection = False
        self.selection_start = (0, 0)
        self.selection_end = (0, 0)
        self.full_screen = None
        self.screen_shot = None
        self.image_panel = None
        self.config = None
        self.tray_control = traycontrol.TrayIcon(self)

        self.RegisterHotKey(0, win32con.MOD_ALT, win32con.VK_F1)
        self.Bind(wx.EVT_HOTKEY, self.on_capture_key, id=0)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_ICONIZE, self.on_iconify)
        self.create_ui()
        self.Center()
        self.Show()

        self.read_config()

    def create_ui(self):
        self.image_panel = imagepanel.ImagePanel(self)

    def read_config(self):
        self.config = Config("config.json")

    def close_capture_frames(self):
        for frame in self.capture_frames:
            frame.Close()

        self.capture_frames = []

    def send(self):
        image = self.screen_shot.ConvertToImage()
        stream = io.BytesIO()
        image.SaveStream(stream, wx.BITMAP_TYPE_PNG)

        files = {
            "image": ("captured.png", stream.getvalue())
        }

        response = requests.post("http://dg-pic.tk/upload_test", files=files)

        print response.text

    def screen_shot_from_selection(self, selection):
        bitmap = wx.EmptyBitmap(selection.width, selection.height)

        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(0, 0, selection.width, selection.height, wx.MemoryDC(self.full_screen), selection.x, selection.y)
        memory.SelectObject(wx.NullBitmap)

        return bitmap

    def set_screen_shot(self, screen_shot):
        self.screen_shot = screen_shot
        self.image_panel.set_bitmap(self.screen_shot)
        self.Refresh()

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
        self.full_screen = self.get_full_screen()

        if not self.in_capture():
            amount = range(wx.Display.GetCount())
            self.capture_frames = [capture.CaptureFrame(self, wx.Display(i), self.full_screen) for i in amount]
        else:
            self.set_screen_shot(self.full_screen)
            self.close_capture_frames()

    def on_iconify(self, event):
        if self.IsIconized() and not self.config.minimize_on_close:  # This is dumb, but absolutely needed
            self.Hide()

    def show(self):
        self.Show()
        self.Restore()

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