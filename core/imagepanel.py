import wx


class ImagePanel(wx.PyScrolledWindow):
    def __init__(self, parent):
        wx.PyScrolledWindow.__init__(self, parent=parent, style=wx.BORDER_SUNKEN)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.bitmap = wx.NullBitmap
        self.drawing_layer = wx.NullBitmap
        self.current_tool = PencilTool()

        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

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

    def set_tool(self, tool):
        self.current_tool = tool

    def set_bitmap(self, bitmap):
        w = bitmap.GetWidth()
        h = bitmap.GetHeight()

        self.bitmap = bitmap
        self.SetScrollbars(10, 10, w / 10, h / 10)
        self.Refresh()

        if self.drawing_layer:
            self.drawing_layer.Destroy()

        self.drawing_layer = wx.EmptyBitmapRGBA(w, h, alpha=0)

    def on_mouse(self, evt):
        if self.current_tool and self.drawing_layer:
            scrolled = self.CalcScrolledPosition(0, 0)

            dc = wx.MemoryDC(self.drawing_layer)
            gc = wx.GraphicsContext.Create(dc)
            gc.Translate(-scrolled[0], -scrolled[1])
            self.current_tool.on_mouse(self, gc, evt)
            dc.SelectObject(wx.NullBitmap)
            dc.Destroy()

            self.Refresh()


class CanvasTool:
    def __init__(self):
        pass

    def on_mouse(self, panel, dc, event):
        pass


class PencilTool(CanvasTool):
    def __init__(self):
        CanvasTool.__init__(self)
        self.pen = wx.Pen(wx.Colour(255, 0, 0))

    def on_mouse(self, panel, gc, event):
        if event.Dragging():
            gc.SetPen(wx.RED_PEN)
            gc.DrawRectangle(event.X, event.Y, 1, 1)