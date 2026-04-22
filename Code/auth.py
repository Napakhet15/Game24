"""
auth.py
handles user accounts - register, login, logout
stores data in users.json
"""

import hashlib
import json
import os


USERS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "users.json")


class User:
    # stores one user's info

    def __init__(self, username: str, password_hash: str, achievements: list):
        self.username = username
        self.password_hash = password_hash  # we never store real password
        self.achievements = achievements    # list of achievement ids

    def to_dict(self) -> dict:
        # convert to dict so we can save to json
        return {
            "username":     self.username,
            "password":     self.password_hash,
            "achievements": self.achievements,
        }

    @classmethod
    def from_dict(cls, d: dict):
        # load user from dict (used when reading json file)
        return cls(
            username=d["username"],
            password_hash=d["password"],
            achievements=d.get("achievements", []),
        )


class UserStore:
    # reads and writes users.json

    def __init__(self, path: str = USERS_PATH):
        self.path = path

    def _load(self) -> list:
        # read users.json and return list of User objects
        if not os.path.isfile(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            # file is broken, start fresh
            return []

        if not isinstance(data, list):
            return []

        return [User.from_dict(d) for d in data if isinstance(d, dict)]

    def _save(self, users: list):
        # write list of users back to json file
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, indent=2)

    def find(self, username: str):
        # find user by username, return None if not found
        for user in self._load():
            if user.username == username:
                return user
        return None

    def register(self, username: str, password: str) -> "User":
        # create new account and save to file
        users = self._load()

        # trim spaces just in case
        username = username.strip()
        password = password.strip()

        # check if username already taken
        for user in users:
            if user.username == username:
                raise ValueError(f"Username '{username}' is already taken.")

        # hash password before saving (never save plain password)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        new_user = User(username=username, password_hash=password_hash, achievements=[])

        users.append(new_user)
        self._save(users)

        return new_user

    def login(self, username: str, password: str):
        # check username and password, return User if correct
        username = username.strip()
        password = password.strip()

        user = self.find(username)
        if user is None:
            return None

        # hash the input and compare to stored hash
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password_hash != password_hash:
            return None  # wrong password

        return user

    def save_user(self, updated_user: "User"):
        # update existing user data in file (used when unlocking achievements)
        users = self._load()

        for i, user in enumerate(users):
            if user.username == updated_user.username:
                users[i] = updated_user
                self._save(users)
                return

        raise ValueError(f"User '{updated_user.username}' not found in store.")


class AuthManager:
    # controls login/logout and keeps track of who is logged in

    def __init__(self, store: UserStore = None):
        self._store = store if store is not None else UserStore()
        self._current_user = None  # None means nobody is logged in

    @property
    def current_user(self):
        # get the currently logged in user
        return self._current_user

    def register(self, username: str, password: str) -> "User":
        # register new user
        user = self._store.register(username, password)
        return user

    def login(self, username: str, password: str) -> bool:
        # try to log in, return True if success
        user = self._store.login(username, password)
        if user is not None:
            self._current_user = user
            return True
        return False

    def logout(self):
        # clear current user
        self._current_user = None
