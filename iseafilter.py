class IseaFilter(object):

    def __init__(self, name):
        self.name = name
        self.data = {}

    def get_filter(self):
        return self.data

    def get_name(self):
        return self.name

    def add_filter(self, key, value):
        self.data[key] = value
