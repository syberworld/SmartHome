class Dsp():

    def __init__(self):
        self.store = {}

    def read(self, path):
        path = path.split(".")
        data = self.store
        for i in range(0, len(path)):
            try:
                data = data[path[i]]
            except():
                return False
        return data

    def write(self, path, value):
        path = path.split(".")
        data = self.store
        for i in range(0, len(path)-1):
            data = data.setdefault(path[i], {})
        data[path[-1]] = value

    def delete(self, path):
        paths = path.split(".")
        del self.read(path.rsplit('.', 1)[0])[paths[-1]]
