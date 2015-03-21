import wx


class ImagePanel(wx.PyScrolledWindow):
    def __init__(self, ui):
        wx.PyScrolledWindow.__init__(self, parent=ui.app, style=wx.BORDER_SUNKEN)
        self.ui = ui
        self.SetBackgroundStyle(wx.BG_STYLE_ERASE)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)
        self.bitmap = wx.NullBitmap

    def set_bitmap(self, bitmap):
        w = bitmap.GetWidth()
        h = bitmap.GetHeight()

        self.bitmap = bitmap
        self.SetScrollbars(10, 10, w / 10, h / 10)
        self.Refresh()

    def on_erase(self, evt):
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        self.PrepareDC(dc)

        dc.Clear()

        if self.bitmap:
            dc.DrawBitmap(self.bitmap, 0, 0)