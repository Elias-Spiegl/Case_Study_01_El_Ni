from tinydb import Query
from database.db import maintenances_table
from datetime import date, timedelta

class Maintenance:
    db_connector = maintenances_table

    def __init__(self, device_id, due_date, cost=0.0,
                 performed=False, performed_date=None, maintenance_id=None):

        self.device_id = device_id
        self.due_date = due_date
        self.cost = cost
        self.performed = performed
        self.performed_date = performed_date
        self.id = maintenance_id

    def store_data(self):
        MQ = Query()

        # Auto-ID MNT-001 ...
        if self.id is None:
            all_m = self.db_connector.all()
            nums = []
            for m in all_m:
                try:
                    nums.append(int(m["id"].split("-")[1]))
                except:
                    pass
            next_num = max(nums) + 1 if nums else 1
            self.id = f"MNT-{next_num:03d}"

        self.db_connector.upsert(
            {
                "id": self.id,
                "device_id": self.device_id,
                "due_date": self.due_date,
                "cost": self.cost,
                "performed": self.performed,
                "performed_date": self.performed_date
            },
            MQ.id == self.id
        )

    def delete(self):
        MQ = Query()
        self.db_connector.remove(MQ.id == self.id)

    @classmethod
    def find_all(cls):
        return cls.db_connector.all()

    @classmethod
    def find_by_device(cls, device_id):
        MQ = Query()
        return cls.db_connector.search(MQ.device_id == device_id)
