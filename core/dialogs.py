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
    def __init__(self, *args, **kwargs):
        super(SettingsDialog, self).__init__(*args, **kwargs)