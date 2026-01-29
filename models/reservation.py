from tinydb import Query
from database.db import reservations_table

class Reservation:
    db_connector = reservations_table

    def __init__(self, device_id, user_email, start_date, end_date, reservation_id=None):
        self.device_id = device_id
        self.user_email = user_email
        self.start_date = start_date
        self.end_date = end_date
        self.id = reservation_id

    def store_data(self):
        ResQ = Query()

        # Auto-ID RES-001 ...
        if self.id is None:
            all_res = self.db_connector.all()
            nums = []
            for r in all_res:
                try:
                    nums.append(int(r["id"].split("-")[1]))
                except:
                    pass
            next_num = max(nums) + 1 if nums else 1
            self.id = f"RES-{next_num:03d}"

        self.db_connector.upsert(
            {
                "id": self.id,
                "device_id": self.device_id,
                "user_email": self.user_email,
                "start_date": self.start_date,
                "end_date": self.end_date
            },
            ResQ.id == self.id
        )

    def delete(self):
        ResQ = Query()
        self.db_connector.remove(ResQ.id == self.id)

    @classmethod
    def find_all(cls):
        return cls.db_connector.all()

    # ---------------------------------------------------
    # Check ob Device verfügbar ist
    # ignore_res_id → wichtig beim Bearbeiten!
    # ---------------------------------------------------
    @classmethod
    def is_device_available(cls, device_id, start_date, end_date, ignore_res_id=None):
        ResQ = Query()
        reservations = cls.db_connector.search(ResQ.device_id == device_id)

        for r in reservations:
            if ignore_res_id and r["id"] == ignore_res_id:
                continue

            # Zeitüberlappung prüfen
            if not (end_date < r["start_date"] or start_date > r["end_date"]):
                return False

        return True
