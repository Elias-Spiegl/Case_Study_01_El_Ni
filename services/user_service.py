from repository.json_repository import JsonRepository

repo = JsonRepository("data/users.json")

def get_users():
    return repo.get_all()

def add_user(user: dict):
    users = repo.get_all()
    users.append(user)
    repo.save_all(users)
