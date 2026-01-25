from models.serializable import Serializable
from database.db import users_table
from datetime import datetime


class User(Serializable):
    db_connector = users_table

    def __init__(
        self,
        id: str,
        name: str,
        creation_date: datetime | None = None,
        last_update: datetime | None = None
    ):
        super().__init__(id, creation_date, last_update)
        self.name = name

    @classmethod
    def instantiate_from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            name=data["name"],
            creation_date=data.get("creation_date"),
            last_update=data.get("last_update"),
        )

    def __str__(self):
        return f"{self.name} ({self.id})"
