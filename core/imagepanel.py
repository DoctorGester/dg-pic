import wx


class ImagePanel(wx.PyScrolledWindow):
    def __init__(self, parent, ui):
        wx.PyScrolledWindow.__init__(self, parent=parent, style=wx.BORDER_SUNKEN)
        self.ui = ui
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.bitmap = wx.NullBitmap
        self.drawing_layer = wx.NullBitmap
        self.tool_layer = wx.NullBitmap
        self.current_tool = None

        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def get_canvas_size(self):
        return self.drawing_layer.GetWidth(), self.drawing_layer.GetHeight()

    def on_size(self, event):
        event.Skip()
        self.Refresh()

    def on_paint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        rect = self.GetUpdateRegion().GetBox()
        dc.SetClippingRect(rect)
        self.PrepareDC(dc)
        dc.Clear()

        if self.bitmap and self.drawing_layer:
            dc.DrawBitmap(self.bitmap, 0, 0)
            dc.DrawBitmap(self.drawing_layer, 0, 0)

            if self.tool_layer:
                dc.DrawBitmap(self.tool_layer, 0, 0)

    def set_tool(self, tool):
        self.current_tool = tool

        if self.drawing_layer:
            self.create_tool_layer()

    def create_tool_layer(self):
        if self.tool_layer:
            self.tool_layer.Destroy()

        w = self.drawing_layer.GetWidth()
        h = self.drawing_layer.GetHeight()

        self.tool_layer = wx.EmptyBitmapRGBA(w, h, alpha=0)

    def set_bitmap(self, bitmap):
        w = bitmap.GetWidth()
        h = bitmap.GetHeight()

        self.bitmap = bitmap
        self.SetScrollbars(10, 10, w / 10, h / 10)
        self.Refresh()

        if self.drawing_layer:
            self.drawing_layer.Destroy()

        self.drawing_layer = wx.EmptyBitmapRGBA(w, h, alpha=0)
        self.create_tool_layer()

    def on_mouse(self, evt):
        if self.current_tool and self.tool_layer:
            scrolled = self.CalcScrolledPosition(0, 0)

            dc = wx.MemoryDC(self.tool_layer)
            gc = wx.GraphicsContext.Create(dc)
            gc.Translate(-scrolled[0], -scrolled[1])
            has_finished = self.current_tool.on_mouse(self, gc, evt)

            dc.SelectObject(wx.NullBitmap)
            dc.Destroy()

            if has_finished:
                dc = wx.MemoryDC(self.drawing_layer)
                dc.DrawBitmap(self.tool_layer, 0, 0)
                dc.SelectObject(wx.NullBitmap)
                dc.Destroy()

                self.create_tool_layer()

            self.Refresh()