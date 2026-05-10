import hashlib
import json
import os


USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")


class User:
    # user info

    def __init__(self, username: str, password_hash: str, achievements: list):
        self.username = username
        self.password_hash = password_hash 
        self.achievements = achievements    # list achievement

    def to_dict(self) -> dict:
        return {
            "username":     self.username,
            "password":     self.password_hash,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, d: dict):
        # load user
        return cls(
            username=d["username"],
            password_hash=d["password"],
            achievements=d.get("achievements", []),
        )


class UserStore:
    # users.json

    def __init__(self, path: str = USERS_PATH):
        self.path = path

    def _load(self) -> list:
        if not os.path.isfile(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return []

        if not isinstance(data, list):
            return []

        return [User.from_dict(d) for d in data if isinstance(d, dict)]

    def _save(self, users: list):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, indent=2)

    def find(self, username: str):
        # find user
        for user in self._load():
            if user.username == username:
                return user
        return None

    def register(self, username: str, password: str) -> "User":
        # create new account 
        users = self._load()

        username = username.strip()
        password = password.strip()

        # check username already taken
        for user in users:
            if user.username == username:
                raise ValueError(f"Username '{username}' is already taken.")

        # hash password 
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password_hash=password_hash, achievements=[])

        users.append(new_user)
        self._save(users)

        return new_user

    def login(self, username: str, password: str):
        # check username password
        username = username.strip()
        password = password.strip()

        user = self.find(username)
        if user is None:
            return None

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password_hash != password_hash:
            return None  # wrong 

        return user

    def save_user(self, updated_user: "User"):
        users = self._load()

        for i, user in enumerate(users):
            if user.username == updated_user.username:
                users[i] = updated_user
                self._save(users)
                return

        raise ValueError(f"User '{updated_user.username}' not found in store.")


class AuthManager:

    def __init__(self, store: UserStore = None):
        self._store = store if store is not None else UserStore()
        self._current_user = None 

    @property
    def current_user(self):
        return self._current_user

    def register(self, username: str, password: str) -> "User":
        # register
        user = self._store.register(username, password)
        return user

    def login(self, username: str, password: str) -> bool:
        # try to log in
        user = self._store.login(username, password)
        if user is not None:
            self._current_user = user
            return True
        return False

    def logout(self):
        # clear user
        self._current_user = None
