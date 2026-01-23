from tinydb import Query
from typing import List, Optional, Self
from datetime import date
from database import DatabaseConnector
from serializable import Serializable

class User(Serializable):  # Erbt von Serializable
    db_connector = DatabaseConnector().get_table("users")

    def __init__(self, email: str, name: str):
        self.email = email
        self.name = name

    def __str__(self):
        return f"{self.name} ({self.email})"

    def store_data(self):
        UserQuery = Query()
        self.db_connector.upsert(self.to_dict(), UserQuery.email == self.email)

    def delete(self) -> bool:
        # Löscht den Nutzer nur, wenn er KEINE Geräte mehr verwaltet.
        all_devices = Device.find_all()
        
        for device in all_devices:
            if device.responsible_person == self.email:
                return False

        UserQuery = Query()
        self.db_connector.remove(UserQuery.email == self.email)
        return True

    @classmethod
    def find_all(cls) -> List[Self]:
        return [cls(**data) for data in cls.db_connector.all()]
    
    @classmethod
    def find_by_email(cls, email: str) -> Optional[Self]:
        UserQuery = Query()
        result = cls.db_connector.search(UserQuery.email == email)
        return cls(**result[0]) if result else None


class Device(Serializable):  # Erbt von Serializable
    db_connector = DatabaseConnector().get_table("devices")

    def __init__(self, name: str, responsible_person: str = None, 
                 next_maintenance: date = None, maintenance_cost: float = 0.0, 
                 id: str = None):
        self.name = name
        self.responsible_person = responsible_person
        self.next_maintenance = next_maintenance if next_maintenance else date.today()
        self.maintenance_cost = maintenance_cost
        self.id = id

    def store_data(self):
        if not self.id:
            self.id = self._generate_id()

        DeviceQuery = Query()
        self.db_connector.upsert(self.to_dict(), DeviceQuery.id == self.id)

    def delete(self):
        DeviceQuery = Query()
        self.db_connector.remove(DeviceQuery.id == self.id)

    def _generate_id(self):
        all_devices = self.db_connector.all()
        if not all_devices:
            return "DEV-001"
        
        numbers = []
        for d in all_devices:
            try:
                numbers.append(int(d["id"].split("-")[1]))
            except (KeyError, IndexError, ValueError):
                continue
        
        next_number = max(numbers) + 1 if numbers else 1
        return f"DEV-{next_number:03d}"

    @classmethod
    def find_all(cls) -> List[Self]:
        return [cls(**d) for d in cls.db_connector.all()]

    @classmethod
    def find_by_id(cls, device_id: str) -> Optional[Self]:
        DeviceQuery = Query()
        result = cls.db_connector.search(DeviceQuery.id == device_id)
        return cls(**result[0]) if result else None