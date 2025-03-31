from abc import ABC, abstractmethod

from feature.requested_feature import RequestedFeature


class DatabaseConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get(self, key) -> RequestedFeature:
        pass

    @abstractmethod
    def set(self, key, value: RequestedFeature):
        pass

    @abstractmethod
    def delete(self, key):
        pass
