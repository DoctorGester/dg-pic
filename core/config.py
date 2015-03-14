import json
import os.path

special_keys = ('file_name', 'transaction', 'data', 'modify_time')


class Config:

    def __init__(self, file_name):
        self.file_name = file_name
        self.transaction = False
        self.data = None
        self.modify_time = 0

        self.load_file()

    def __getattr__(self, item):
        if self.modify_time != os.path.getmtime(self.file_name):
            self.load_file()

        if item in self.data:
            return self.data[item]

        return None

    def __setattr__(self, key, value):
        if key in special_keys:
            self.__dict__[key] = value
            return

        self.data[key] = value

        if not self.transaction:
            self.save_file()

    def load_file(self):
        if not os.path.isfile(self.file_name):
            file_data = open(self.file_name, 'w+')
        else:
            file_data = open(self.file_name, 'r+')

        self.modify_time = os.path.getmtime(self.file_name)

        try:
            self.data = json.load(file_data)
        except ValueError:
            self.data = {}
            json.dump(self.data, file_data)

        file_data.close()

    def save_file(self):
        file_data = open(self.file_name, 'w+')
        json.dump(self.data, file_data, sort_keys=True, indent=4)
        file_data.close()

    def begin_transaction(self):
        self.transaction = True

    def end_transaction(self):
        if not self.transaction:
            return

        self.transaction = False
        self.save_file()