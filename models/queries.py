from models.device import Device

class Queries:
    @staticmethod
    def find_devices():
        devices = Device.db_connector.all()
        return [d["name"] for d in devices]
