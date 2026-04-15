"""
User management module with CRUD operations for user data.

This module provides functionality to manage user records in a SQLite database,
following the Single Responsibility Principle (SRP) by separating concerns
into distinct classes.

Example:
    >>> from user_manager import UserRepository
    >>> repo = UserRepository("users.db")
    >>> user = repo.get_by_id(1)
    >>> print(user.name)
"""

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import sqlite3
except ImportError:
    raise ImportError("sqlite3 is required. Use Python 3.x.")


@dataclass
class User:
    """Represents a user entity with id, name, and email attributes."""

    id: int
    name: str
    email: str

    def __post_init__(self) -> None:
        """Validates user data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("User name cannot be empty.")
        if not self.email or "@" not in self.email:
            raise ValueError("Invalid email address.")

    def to_dict(self) -> dict:
        """Converts the user instance to a dictionary."""
        return {"id": self.id, "name": self.name, "email": self.email}


class DatabaseError(Exception):
    """Base exception for database-related errors."""

    pass


class UserNotFoundError(DatabaseError):
    """Raised when a user is not found in the database."""

    pass


class UserRepository:
    """
    Repository class for managing user data in a SQLite database.

    Implements the Repository pattern to abstract database operations
    from business logic, following the Dependency Inversion Principle (DIP).

    Attributes:
        _db_path: Path to the SQLite database file.

    Example:
        >>> repo = UserRepository("users.db")
        >>> user = repo.get_by_id(1)
    """

    def __init__(self, db_path: str) -> None:
        """
        Initializes the UserRepository with the specified database path.

        Args:
            db_path: Path to the SQLite database file.
        """
        self._db_path = db_path
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Creates and returns a database connection."""
        return sqlite3.connect(self._db_path)

    def _init_database(self) -> None:
        """Initializes the database schema if it doesn't exist."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)
            conn.commit()
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieves a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            User instance if found, None otherwise.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(id=row[0], name=row[1], email=row[2])
            return None
        finally:
            conn.close()

    def get_all(self) -> list[User]:
        """
        Retrieves all users from the database.

        Returns:
            List of User instances.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email FROM users")
            return [
                User(id=row[0], name=row[1], email=row[2]) for row in cursor.fetchall()
            ]
        finally:
            conn.close()

    def create(self, name: str, email: str) -> User:
        """
        Creates a new user in the database.

        Args:
            name: The user's name.
            email: The user's email address.

        Returns:
            The created User instance with generated ID.

        Raises:
            DatabaseError: If the user creation fails.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name.strip(), email.strip()),
            )
            conn.commit()
            user_id = cursor.lastrowid
            if user_id is None:
                raise DatabaseError("Failed to retrieve new user ID.")
            return User(id=user_id, name=name, email=email)
        except sqlite3.Error as e:
            conn.rollback()
            raise DatabaseError(f"Failed to create user: {e}")
        finally:
            conn.close()

    def delete(self, user_id: int) -> bool:
        """
        Deletes a user by their ID.

        Args:
            user_id: The unique identifier of the user to delete.

        Returns:
            True if the user was deleted, False if not found.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            conn.rollback()
            raise DatabaseError(f"Failed to delete user: {e}")
        finally:
            conn.close()


def get_user_data(user_id: int) -> Optional[dict]:
    """
    Legacy function to get user data by ID.

    This function is maintained for backward compatibility.
    Consider using UserRepository for new code.

    Args:
        user_id: The unique identifier of the user.

    Returns:
        Dictionary with user data if found, None otherwise.
    """
    repo = UserRepository("users.db")
    user = repo.get_by_id(user_id)
    return user.to_dict() if user else None


def save_user(name: str, email: str) -> int:
    """
    Legacy function to save a new user.

    This function is maintained for backward compatibility.
    Consider using UserRepository for new code.

    Args:
        name: The user's name.
        email: The user's email address.

    Returns:
        The ID of the created user.
    """
    repo = UserRepository("users.db")
    user = repo.create(name, email)
    return user.id


def delete_user(user_id: int) -> bool:
    """
    Legacy function to delete a user by ID.

    This function is maintained for backward compatibility.
    Consider using UserRepository for new code.

    Args:
        user_id: The unique identifier of the user to delete.

    Returns:
        True if the user was deleted.
    """
    repo = UserRepository("users.db")
    return repo.delete(user_id)
