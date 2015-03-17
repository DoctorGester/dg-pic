import io
import wx
import json
import requests
import threading
from requests.packages.urllib3.filepost import encode_multipart_formdata

wxEVT_UPLOAD_FINISHED = wx.NewEventType()
wxEVT_UPLOAD_PROGRESS = wx.NewEventType()
EVT_UPLOAD_FINISHED = wx.PyEventBinder(wxEVT_UPLOAD_FINISHED, 1)
EVT_UPLOAD_PROGRESS = wx.PyEventBinder(wxEVT_UPLOAD_PROGRESS, 1)


class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__


class BufferReader(io.BytesIO):
    def __init__(self, buf=b'', app=None):
        self.app = app
        self.progress = 0
        self.len = len(buf)
        io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self.len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, n)
        self.progress += int(len(chunk))
        if self.app:
            try:
                wx.PostEvent(self.app, UploadProgressEvent(self.len, self.progress))
            except:  # catches exception from the callback
                raise CancelledError("The upload was cancelled.")
        return chunk


class UploadFinishedEvent(wx.PyCommandEvent):
    def __init__(self, response):
        wx.PyCommandEvent.__init__(self, wxEVT_UPLOAD_FINISHED, -1)
        self.response = response

    def text(self):
        if isinstance(self.response, requests.RequestException):
            return json.dumps({"success": False, "message": str(self.response)})

        return self.response.text


class UploadProgressEvent(wx.PyCommandEvent):
    def __init__(self, total, uploaded):
        wx.PyCommandEvent.__init__(self, wxEVT_UPLOAD_PROGRESS, -1)
        self.total = total
        self.uploaded = uploaded


class UploadThread(threading.Thread):
    def __init__(self, app, url, files):
        threading.Thread.__init__(self)
        self.app = app
        self.url = url
        self.files = files

    def run(self):
        (data, content_type) = encode_multipart_formdata(self.files)

        headers = {
            "Content-Type": content_type
        }

        body = BufferReader(data, self.app)

        try:
            response = requests.post(self.url, data=body, headers=headers)
            wx.PostEvent(self.app, UploadFinishedEvent(response))
        except requests.RequestException, err:
            wx.PostEvent(self.app, UploadFinishedEvent(err))


def upload_file(app, url, files):
    thread = UploadThread(app, url, files)
    thread.start()