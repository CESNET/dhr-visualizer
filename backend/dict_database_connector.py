from database_connector import DatabaseConnector

class DictDatabaseConnector(DatabaseConnector):
    def __init__(self):
        self.db = {}

    def connect(self):
        pass

    def get(self, key):
        if key in self.db:
            return self.db.get(key)
        return None

    def set(self, key, value):
        self.db[key] = value

    def delete(self, key):
        if key in self.db:
            del self.db[key]
