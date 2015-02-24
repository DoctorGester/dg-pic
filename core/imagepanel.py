import wx


class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundStyle(wx.BG_STYLE_ERASE)
        self.frame = parent
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.on_erase)
        self.bitmap = wx.NullBitmap

    def set_bitmap(self, bitmap):
        self.bitmap = bitmap
        self.Refresh()

    def on_erase(self, evt):
        dc = evt.GetDC()

        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)

        dc.Clear()

        if self.bitmap:
            dc.DrawBitmap(self.bitmap, 0, 0)