import os
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import Serializer, SerializationMiddleware
from datetime import datetime, date

class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime
    def encode(self, obj):
        return obj.isoformat()
    def decode(self, s):
        return datetime.fromisoformat(s)

class DateSerializer(Serializer):
    OBJ_CLASS = date
    def encode(self, obj):
        return obj.isoformat()
    def decode(self, s):
        return date.fromisoformat(s)

class DatabaseConnector:
    __instance = None
    
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            # Speicherort: data Ordner oder direkt
            cls.__instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory_db.json')
            
            # Serializer aufsetzen
            cls.__instance.serializer = SerializationMiddleware(JSONStorage)
            cls.__instance.serializer.register_serializer(DateTimeSerializer(), 'TinyDateTime')
            cls.__instance.serializer.register_serializer(DateSerializer(), 'TinyDate')
            
        return cls.__instance
    
    def get_table(self, table_name: str):
        return TinyDB(self.path, storage=self.serializer).table(table_name)