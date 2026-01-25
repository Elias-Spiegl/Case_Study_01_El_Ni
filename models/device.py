class Device(Serializable):
    db_connector = devices_table

    def __init__(
        self,
        id: str,
        name: str,
        managed_by_user_id: str,
        creation_date=None,
        last_update=None,
        is_active=True,
        end_of_life=None
    ):
        super().__init__(id, creation_date, last_update)
        self.name = name
        self.managed_by_user_id = managed_by_user_id
        self.is_active = is_active
        self.end_of_life = end_of_life

    @classmethod
    def instantiate_from_dict(cls, data: dict):
        return cls(**data)

    def __str__(self):
        return f"{self.name} ({self.id})"
