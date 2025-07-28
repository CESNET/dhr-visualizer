from pymongo import MongoClient
from database.database_connector import DatabaseConnector
from fastapi.logger import logger
import variables

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
        logger.debug(f"[{__name__}]: MongoDB collections: {self.db.list_collection_names()}")
        if self.collection_name not in self.db.list_collection_names():
            self.collection = self.db.create_collection(self.collection_name)
        else:
            self.collection = self.db[self.collection_name]

    def get(self, key):
        document = self.collection.find_one({"_id": key})
        return document["value"] if document else None

    def set(self, key, value):
        self.collection.update_one(
            {"_id": key},
            {"$set": {"value": value}},
            upsert=True
        )

    def delete(self, key):
        self.collection.delete_one({"_id": key})
