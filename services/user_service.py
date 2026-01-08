from repository.json_repository import JsonRepository
from .device_service import get_devices, update_device

repo = JsonRepository("data/users.json")

def get_users():
    return repo.get_all()

def add_user(user: dict):
    users = repo.get_all()
    users.append(user)
    repo.save_all(users)

def update_user(user_email: str, updated_user: dict) -> bool:
    users = repo.get_all()

    for i, u in enumerate(users):
        if u["email"] == user_email:
            users[i] = updated_user
            repo.save_all(users)
            return True

    return False

def delete_user(user_email: str) -> bool:
    users = repo.get_all()

    new_users = [u for u in users if u["email"] != user_email]

    if len(new_users) == len(users):
        return False

    repo.save_all(new_users)
    return True

def delete_user(user_email: str) -> bool:
    # 1) Geräte umhängen
    devices = get_devices()
    for d in devices:
        if d.get("responsible_person") == user_email:
            update_device(
                d["id"],
                {
                    **d,
                    "responsible_person": None
                }
            )

    # 2) User löschen
    users = repo.get_all()
    new_users = [u for u in users if u["email"] != user_email]

    if len(new_users) == len(users):
        return False

    repo.save_all(new_users)
    return True
