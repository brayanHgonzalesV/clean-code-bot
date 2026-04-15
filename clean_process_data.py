"""
Data processing application with authentication.

Refactored to follow SOLID principles:
- S: Single Responsibility - Separate classes for auth, storage, UI
- O: Open/Closed - Easy to extend with new storage backends
- L: Liskov Substitution - All storage implementations work the same
- I: Interface Segregation - Focused interfaces for each role
- D: Dependency Inversion - Depend on abstractions, not concretions
"""

import datetime
from abc import ABC, abstractmethod
from typing import Optional


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class DataError(Exception):
    """Raised when data operation fails."""

    pass


class User:
    """User entity."""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


class DataItem:
    """Individual data item."""

    def __init__(self, item_id: int, value: str, created_at: str):
        self.id = item_id
        self.value = value
        self.created_at = created_at

    def __str__(self) -> str:
        return f"Item: {self.id} - {self.value} at {self.created_at}"

    def to_dict(self) -> dict:
        return {"id": self.id, "val": self.value, "date": self.created_at}


class IAuthenticator(ABC):
    """Interface for authentication (ISP)."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> bool:
        pass


class IStorage(ABC):
    """Interface for data storage (OCP)."""

    @abstractmethod
    def save(self, items: list[DataItem]) -> None:
        pass

    @abstractmethod
    def load(self) -> list[DataItem]:
        pass


class FileStorage(IStorage):
    """File-based storage implementation."""

    def __init__(self, filename: str = "data.txt"):
        self.filename = filename

    def save(self, items: list[DataItem]) -> None:
        try:
            with open(self.filename, "w") as f:
                f.write(str([item.to_dict() for item in items]))
        except IOError as e:
            raise DataError(f"Failed to save data: {e}")

    def load(self) -> list[DataItem]:
        try:
            with open(self.filename, "r") as f:
                content = f.read()
                return [] if not content else []
        except FileNotFoundError:
            return []
        except IOError as e:
            raise DataError(f"Failed to load data: {e}")


class CredentialsAuthenticator(IAuthenticator):
    """Authentication using stored credentials."""

    def __init__(self, users: list[User]):
        self.users = {u.username: u.password for u in users}

    def authenticate(self, username: str, password: str) -> bool:
        stored = self.users.get(username)
        if stored is None:
            return False
        return stored == password


class DataManager:
    """
    Manages data items (SRP - only manages data).
    """

    def __init__(self, storage: IStorage):
        self.storage = storage
        self.items: list[DataItem] = []

    def add(self, value: str) -> None:
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item_id = len(self.items) + 1
        new_item = DataItem(item_id, value, now)
        self.items.append(new_item)
        print("Added.")

    def show(self) -> None:
        if not self.items:
            print("No items.")
            return
        for item in self.items:
            print(str(item))

    def save(self) -> None:
        self.storage.save(self.items)
        print("Saved.")

    def load(self) -> None:
        self.items = self.storage.load()
        print("Loaded.")


class Application:
    """
    Main application (orchestrates other classes).
    """

    def __init__(self, authenticator: IAuthenticator, data_manager: DataManager):
        self.authenticator = authenticator
        self.data_manager = data_manager

    def run(self) -> None:
        username = input("User: ")
        password = input("Pass: ")

        if not self.authenticator.authenticate(username, password):
            print("Wrong!")
            return

        print("Welcome")

        commands = {
            "add": lambda: self.data_manager.add(input("Value: ")),
            "show": lambda: self.data_manager.show(),
            "save": lambda: self.data_manager.save(),
            "load": lambda: self.data_manager.load(),
        }

        while True:
            cmd = input("What to do? (add/show/save/load/exit): ")
            if cmd == "exit":
                break
            if cmd in commands:
                commands[cmd]()
            else:
                print("Unknown command.")


def main() -> None:
    users = [User("admin", "12345")]
    authenticator = CredentialsAuthenticator(users)
    storage = FileStorage("data.txt")
    data_manager = DataManager(storage)
    app = Application(authenticator, data_manager)
    app.run()


if __name__ == "__main__":
    main()
