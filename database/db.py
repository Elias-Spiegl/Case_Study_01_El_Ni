from tinydb import TinyDB
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer, DateSerializer

serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), "TinyDateTime")
serialization.register_serializer(DateSerializer(), "TinyDate")

db = TinyDB("database/database.json", storage=serialization)

users_table = db.table("users")
devices_table = db.table("devices")
reservations_table = db.table("reservations")
maintenances_table = db.table("maintenances")


