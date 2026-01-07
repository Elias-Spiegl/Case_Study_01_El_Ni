from repository.json_repository import JsonRepository

repo = JsonRepository("data/devices.json")

def get_devices():
    return repo.get_all()

def add_device(device: dict):
    devices = repo.get_all()
    devices.append(device)
    repo.save_all(devices)

def update_device(device_id: str, updated_device: dict):
    devices = repo.get_all()

    for i, d in enumerate(devices):
        if d["id"] == device_id:
            devices[i] = updated_device
            repo.save_all(devices)
            return True

    return False
