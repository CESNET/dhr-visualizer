from abc import ABC, abstractmethod

from feature.processing.processed_feature import ProcessedFeature


class DatabaseConnector(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def get(self, key) -> ProcessedFeature:
        pass

    @abstractmethod
    def set(self, key, value: ProcessedFeature):
        pass

    @abstractmethod
    def delete(self, key):
        pass
