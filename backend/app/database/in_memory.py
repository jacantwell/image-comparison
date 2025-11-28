import uuid
from threading import Lock

from app.models import ComparisonResult

from .base import BaseDatabase


class InMemoryDatabase(BaseDatabase):
    """Thread-safe in-memory storage for comparison results."""

    def __init__(self):
        """Initialize the in-memory database with an empty storage dict and lock."""
        self._sessions: dict[str, ComparisonResult] = {}
        self._lock = Lock()

    async def create(self, result: ComparisonResult) -> str:
        """
        Store a comparison result in memory.

        Args:
            result: The comparison result to store

        Returns:
            Unique identifier for the stored result
        """

        comparison_id = str(uuid.uuid4())

        with self._lock:
            self._sessions[comparison_id] = result

        return comparison_id

    async def read(self, id: str) -> ComparisonResult:
        """
        Retrieve a comparison result by its identifier.

        Args:
            id: The unique identifier of the result

        Returns:
            The comparison result
        """

        with self._lock:
            result = self._sessions.get(id)

        if not result:
            raise ValueError(f"No result found for ID {id}")

        return result

    async def read_all(self) -> list[str]:
        """
        Retrieve all stored comparison result identifiers.

        Returns:
            List of all comparison IDs (empty list if no results stored)
        """
        with self._lock:
            ids = list(self._sessions.keys())

        return ids
