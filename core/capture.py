import wx


class CaptureFrame(wx.Frame):
    def __init__(self, parent, display, screen_bitmap):
        wx.Frame.__init__(self, parent, -1, "capture", style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)
        self.parent = parent
        self.display = display
        self.screen_bitmap = screen_bitmap
        self.image, self.original = self.create_background()
        self.should_redraw = False

        # memory dc to draw off-screen
        self.mdc = None

        self.Bind(wx.EVT_KILL_FOCUS, self.on_lose_focus)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)
        self.Bind(wx.EVT_MOTION, self.on_motion)
        self.Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        self.Bind(wx.EVT_KEY_UP, self.on_key_up)

        self.SetCursor(wx.StockCursor(wx.CURSOR_CROSS))
        self.SetPosition(display.GetGeometry().GetTopLeft())
        self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)

        wx.CallLater(20, self.SetFocus)

        self.on_timer()

    def create_background(self):
        rect = self.display.GetGeometry()
        w, h = rect.GetSize()

        dc_from = wx.MemoryDC(self.screen_bitmap)
        bitmap = wx.EmptyBitmap(w, h)
        original = wx.EmptyBitmap(w, h)

        args = (0, 0, w, h, dc_from, rect.x, rect.y)

        memory = wx.MemoryDC()
        memory.SelectObject(bitmap)
        memory.Blit(*args)
        gc = wx.GraphicsContext.Create(memory)

        if gc:
            gc.SetBrush(wx.Brush(wx.Colour(255, 255, 255, 90)))
            gc.DrawRectangle(0, 0, w, h)

        memory.SelectObject(original)
        memory.Blit(*args)
        memory.SelectObject(wx.NullBitmap)

        return bitmap, original

    def on_key_up(self, event):
        if event.GetKeyCode() is wx.WXK_ESCAPE:
            self.parent.close_capture_frames()

        event.Skip()

    def on_left_down(self, event):
        self.parent.on_left_down(self.display, event)
        event.Skip()

    def on_left_up(self, event):
        self.parent.on_left_up(self.display, event)
        event.Skip()

    def on_motion(self, event):
        self.parent.on_motion(self.display, event)

        event.Skip()

    def on_right_up(self, event):
        self.parent.close_capture_frames()
        event.Skip()

    def on_timer(self):
        if self.mdc and self.should_redraw:
            self.should_redraw = False
            self.redraw()

        wx.CallLater(20, self.on_timer)

    def on_size(self, event):
        # re-create memory dc to fill window
        w, h = self.GetClientSize()
        self.mdc = wx.MemoryDC(wx.EmptyBitmap(w, h))
        self.redraw()

    def on_erase(self, event):
        # don't do any erasing to avoid flicker
        pass

    def on_paint(self, event):
        # just blit the memory dc
        dc = wx.PaintDC(self)

        if not self.mdc:
            return

        w, h = self.mdc.GetSize()
        dc.Blit(0, 0, w, h, self.mdc, 0, 0)

    def redraw(self):
        # do the actual drawing on the memory dc here
        dc = self.mdc
        dc.Clear()

        if self.image:
            dc.DrawBitmap(self.image, 0, 0)
            dc.SetPen(wx.Pen(wx.BLACK, 2))

            if self.parent.in_selection:
                selection = self.parent.get_selection_for_display(self.display)
                sub_dc = wx.MemoryDC(self.original)
                dc.Blit(selection.x, selection.y, selection.width, selection.height, sub_dc, selection.x, selection.y)

                dc.SetBrush(wx.Brush(None, wx.BRUSHSTYLE_TRANSPARENT))
                dc.SetPen(wx.Pen(wx.BLACK, 1))
                dc.DrawRectangleRect(selection)

        self.Refresh()

    def on_lose_focus(self, event):
        target = event.GetWindow()

        if target is None or target is self.parent:
            self.parent.close_capture_frames()