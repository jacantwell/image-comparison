from enum import Enum


class VisualationType(str, Enum):
    HEATMAP = "heatmap"
    CONTOUR = "contour"

    @classmethod
    def to_list(cls) -> list[str]:
        return [item.value for item in cls]
