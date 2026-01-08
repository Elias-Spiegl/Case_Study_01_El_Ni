from repository.json_repository import JsonRepository

repo = JsonRepository("data/devices.json")

def get_devices():
    return repo.get_all()

def add_device(device: dict):
    devices = repo.get_all()
    device["id"] = generate_next_device_id(devices)
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

def generate_next_device_id(devices):

    # Erzeugt eine fortlaufende Geräte-ID im Format DEV-001, DEV-002, ...
    if not devices:
        return "DEV-001"

    numbers = []
    for d in devices:
        try:
            numbers.append(int(d["id"].split("-")[1]))
        except (KeyError, IndexError, ValueError):
            continue

    next_number = max(numbers) + 1 if numbers else 1
    return f"DEV-{next_number:03d}"


def delete_device(device_id: str) -> bool:
    devices = repo.get_all()

    new_devices = [d for d in devices if d["id"] != device_id]

    if len(new_devices) == len(devices):
        return False  # nichts gelöscht

    repo.save_all(new_devices)
    return True

def unassign_devices_from_user(user_email: str):
    devices = repo.get_all()

    for d in devices:
        if d.get("responsible_person") == user_email:
            d["responsible_person"] = None

    repo.save_all(devices)
