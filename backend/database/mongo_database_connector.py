from pymongo import MongoClient
from database.database_connector import DatabaseConnector
from fastapi.logger import logger
import variables
from feature.processing.sentinel1_feature import Sentinel1Feature
from feature.processing.sentinel2_feature import Sentinel2Feature


class MongoDatabaseConnector(DatabaseConnector):
    def __init__(self):
        self._client = None
        self._db = None
        self._collection = None
        self._mongo_uri = variables.MONGO_URI
        self._database_name = variables.MONGO_DB
        self._collection_name = "products"

    def connect(self):
        self._client = MongoClient(self._mongo_uri)
        self._db = self._client[self._database_name]
        if self._collection_name not in self._db.list_collection_names():
            self._collection = self._db.create_collection(self._collection_name)
        else:
            self._collection = self._db[self._collection_name]

    def get(self, key):
        document = self._collection.find_one({"_id": key})
        if not document:
            return None
        if document["platform"] == "SENTINEL-2":
            return Sentinel2Feature.from_dict(document)
        if document["platform"] == "SENTINEL-1":
            return Sentinel1Feature.from_dict(document)
        logger.error(f"[{__name__}]: Unknown platform: {document['platform']}")
        raise Exception(f"Unknown platform: {document['platform']} found in database for key: {key}!")

    def set(self, key, value):
        self._collection.update_one(
            {"_id": key},
            {"$set": value.to_dict()},
            upsert=True
        )

    def delete(self, key):
        logger.debug(f"[{__name__}]: Deleting MongoDB document with key: {key}")
        self._collection.delete_one({"_id": key})
