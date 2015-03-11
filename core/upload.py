import io
import requests
from requests.packages.urllib3.filepost import encode_multipart_formdata


class CancelledError(Exception):
    def __init__(self, msg):
        self.msg = msg
        Exception.__init__(self, msg)

    def __str__(self):
        return self.msg

    __repr__ = __str__


class BufferReader(io.BytesIO):
    def __init__(self, buf=b'', callback=None):
        self.callback = callback
        self.progress = 0
        self.len = len(buf)
        io.BytesIO.__init__(self, buf)

    def __len__(self):
        return self.len

    def read(self, n=-1):
        chunk = io.BytesIO.read(self, n)
        self.progress += int(len(chunk))
        if self.callback:
            try:
                self.callback(size=self.len, progress=self.progress)
            except:  # catches exception from the callback
                raise CancelledError("The upload was cancelled.")
        return chunk


def upload_file(url, files, callback):

    (data, content_type) = encode_multipart_formdata(files)

    headers = {
        "Content-Type": content_type
    }

    body = BufferReader(data, callback)
    return requests.post(url, data=body, headers=headers)