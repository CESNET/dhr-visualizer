from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def delete(self, key):
        pass
