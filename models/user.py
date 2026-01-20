from tinydb import Query
from database.db import users_table

class User:
    db_connector = users_table   # Class Attribute

    def __init__(self, name, email):
        self.name = name
        self.id = email            # Email = eindeutige ID

    def store_data(self):
        UserQ = Query()
        self.db_connector.upsert(
            {"name": self.name, "email": self.id},
            UserQ.email == self.id
        )

    def delete(self):
        UserQ = Query()
        self.db_connector.remove(UserQ.email == self.id)

    @classmethod
    def find_all(cls):
        return cls.db_connector.all()

    @classmethod
    def find_by_attribute(cls, attr, value):
        UserQ = Query()
        return cls.db_connector.search(getattr(UserQ, attr) == value)

    def __str__(self):
        return f"{self.name} ({self.id})"
