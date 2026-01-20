from tinydb import Query
from datetime import datetime
from database.db import devices_table


class Device:
    db_connector = devices_table

    def __init__(self, name, managed_by_user_id,
                 creation_date=None, last_update=None,
                 is_active=True, end_of_life=None, device_id=None):

        self.device_name = name
        self.managed_by_user_id = managed_by_user_id
        self.creation_date = creation_date or datetime.now()
        self.last_update = last_update or datetime.now()
        self.is_active = is_active
        self.end_of_life = end_of_life
        self.id = device_id

    def store_data(self):
        DeviceQ = Query()

        # Auto-ID wie bisher DEV-001, DEV-002 ...
        if self.id is None:
            all_devices = self.db_connector.all()
            numbers = []
            for d in all_devices:
                try:
                    numbers.append(int(d["id"].split("-")[1]))
                except:
                    pass
            next_number = max(numbers) + 1 if numbers else 1
            self.id = f"DEV-{next_number:03d}"

        self.db_connector.upsert(
            {
                "id": self.id,
                "name": self.device_name,
                "responsible_person": self.managed_by_user_id,
                "creation_date": self.creation_date,
                "last_update": datetime.now(),
                "is_active": self.is_active,
                "end_of_life": self.end_of_life
            },
            DeviceQ.id == self.id
        )

    def delete(self):
        DeviceQ = Query()
        self.db_connector.remove(DeviceQ.id == self.id)

    @classmethod
    def find_all(cls):
        return cls.db_connector.all()

    @classmethod
    def find_by_attribute(cls, attr, value):
        DeviceQ = Query()
        return cls.db_connector.search(getattr(DeviceQ, attr) == value)

    def set_managed_by_user_id(self, user_id):
        self.managed_by_user_id = user_id
        self.store_data()
