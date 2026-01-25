from tinydb import Query
from database.db import users_table, devices_table
from models.user import User
from models.device import Device


# -----------------------------------------------------------------------------
# USER QUERIES
# -----------------------------------------------------------------------------

class UserQueries:

    @staticmethod
    def save(user: User):
        UserQ = Query()
        users_table.upsert(
            user.serialize(),
            UserQ.id == user.id
        )

    @staticmethod
    def delete(user_id: str):
        UserQ = Query()
        users_table.remove(UserQ.id == user_id)

    @staticmethod
    def find_all() -> list[User]:
        return [User.deserialize(u) for u in users_table.all()]

    @staticmethod
    def find_by_id(user_id: str) -> User | None:
        UserQ = Query()
        data = users_table.get(UserQ.id == user_id)
        return User.deserialize(data) if data else None


# -----------------------------------------------------------------------------
# DEVICE QUERIES
# -----------------------------------------------------------------------------

class DeviceQueries:

    @staticmethod
    def save(device: Device):
        DeviceQ = Query()
        devices_table.upsert(
            device.serialize(),
            DeviceQ.id == device.id
        )

    @staticmethod
    def delete(device_id: str):
        DeviceQ = Query()
        devices_table.remove(DeviceQ.id == device_id)

    @staticmethod
    def find_all() -> list[Device]:
        return [Device.deserialize(d) for d in devices_table.all()]

    @staticmethod
    def find_by_id(device_id: str) -> Device | None:
        DeviceQ = Query()
        data = devices_table.get(DeviceQ.id == device_id)
        return Device.deserialize(data) if data else None

    @staticmethod
    def find_by_user(user_id: str) -> list[Device]:
        DeviceQ = Query()
        return [
            Device.deserialize(d)
            for d in devices_table.search(DeviceQ.managed_by_user_id == user_id)
        ]
