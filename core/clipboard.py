import wx


def get_data():
    data = None
    try:
        if wx.TheClipboard.Open():
            if wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_TEXT)):
                do = wx.TextDataObject()
                wx.TheClipboard.GetData(do)
                data = do.GetText()
            elif wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_BITMAP)):
                do = wx.BitmapDataObject()
                wx.TheClipboard.GetData(do)
                data = do.GetBitmap()
            wx.TheClipboard.Close()
    except StandardError:
        data = None
    return data


def set_data(data):
    try:
        if wx.TheClipboard.Open():
            if isinstance(data, (str, unicode)):
                do = wx.TextDataObject()
                do.SetText(data)
                wx.TheClipboard.SetData(do)
            elif isinstance(data, wx.Bitmap):
                do = wx.BitmapDataObject()
                do.SetBitmap(data)
                wx.TheClipboard.SetData(do)
            wx.TheClipboard.Close()
    except StandardError:
        pass