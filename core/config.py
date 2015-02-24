import json
import os.path

special_keys = ('file_name', 'transaction', 'data')


class Config:

    def __init__(self, file_name):
        if not os.path.isfile(file_name):
            file_data = open(file_name, 'w+')
        else:
            file_data = open(file_name, 'r+')

        self.file_name = file_name
        self.transaction = False

        try:
            self.data = json.load(file_data)
        except ValueError:
            self.data = {}
            json.dump(self.data, file_data)

        file_data.close()

    def __getattr__(self, item):
        return self.data[item]

    def __setattr__(self, key, value):
        if key in special_keys:
            self.__dict__[key] = value
            return

        self.data[key] = value

        if not self.transaction:
            self.save_file()

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