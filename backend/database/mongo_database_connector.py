from pymongo import MongoClient
from database.database_connector import DatabaseConnector
from fastapi.logger import logger
import variables
from feature.processing.sentinel1_feature import Sentinel1Feature
from feature.processing.sentinel2_feature import Sentinel2Feature


class MongoDatabaseConnector(DatabaseConnector):
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.mongo_uri = variables.MONGO__URI
        self.database_name = variables.MONGO__DB
        self.collection_name = "products"

    def connect(self):
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client[self.database_name]
        if self.collection_name not in self.db.list_collection_names():
            self.collection = self.db.create_collection(self.collection_name)
        else:
            self.collection = self.db[self.collection_name]

    def get(self, key):
        document = self.collection.find_one({"_id": key})
        if not document:
            return None
        if document["platform"] == "SENTINEL-2":
            return Sentinel2Feature.from_dict(document)
        if document["platform"] == "SENTINEL-1":
            return Sentinel1Feature.from_dict(document)
        logger.error(f"[{__name__}]: Unknown platform: {document['platform']}")
        raise Exception(f"Unknown platform: {document['platform']} found in database for key: {key}!")

    def set(self, key, value):
        # logger.debug(f"[{__name__}]: Setting to mongo: {value.to_dict()}")
        self.collection.update_one(
            {"_id": key},
            {"$set": value.to_dict()},
            upsert=True
        )

    def delete(self, key):
        logger.debug(f"[{__name__}]: Deleting MongoDB document with key: {key}")
        self.collection.delete_one({"_id": key})
