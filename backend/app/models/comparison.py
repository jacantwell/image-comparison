from enum import Enum
from typing import Optional

from cv2.typing import MatLike
from pydantic import BaseModel, ConfigDict


class ComparisonType(str, Enum):
    PIXEL = "pixel"
    STRUCTUAL = "structual"

    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]


class ComparisonResult(BaseModel):
    score: float
    map: MatLike
    visualisation: Optional[bytes] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


# class PixelComparisonResult(BaseComparisonResult):
#     gray_difference_map: MatLike
#     binary_difference_map: MatLike


# class StructualComparisonResult(BaseComparisonResult):
#     gray_difference_map: MatLike
#     binary_difference_map: MatLike
