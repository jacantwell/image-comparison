from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.models import ComparisonResult


class BaseVisualiser(ABC):

    @abstractmethod
    def visualise(
        self, img1: bytes, img2: bytes, comparison: ComparisonResult
    ) -> bytes:
        pass
