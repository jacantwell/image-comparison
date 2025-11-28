from abc import ABC, abstractmethod

from app.models import ComparisonResult


class BaseDatabase(ABC):
    """Abstract base class for database operations."""

    @abstractmethod
    async def create(self, result: ComparisonResult) -> str:
        """
        Store a comparison result and return its unique identifier.

        Args:
            result: The comparison result to store

        Returns:
            Unique identifier for the stored result
        """
        pass

    @abstractmethod
    async def read(self, id: str) -> ComparisonResult:
        """
        Retrieve a comparison result by its identifier.

        Args:
            id: The unique identifier of the result

        Returns:
            The comparison result
        """
        pass

    @abstractmethod
    async def read_all(self) -> list[str]:
        """
        Retrieve all stored comparison result identifiers.

        Returns:
            List of all comparison IDs
        """
        pass
