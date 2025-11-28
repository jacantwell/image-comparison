from abc import ABC, abstractmethod

from app.models import ComparisonResult


class BaseComparer(ABC):

    def __init__(self, sensitivity: int):
        """
        All comparers must have a sensitivity parameter which is input as an integer percentage.
        """
        self.sensitivity = sensitivity

    @abstractmethod
    def compare(self, img1: bytes, img2: bytes) -> ComparisonResult:
        pass
