from app.lib.comparison import BaseComparer, PixelComparer, SSIMComparer
from app.lib.visualisation import (BaseVisualiser, ContourVisualiser,
                                   HeatmapVisualiser)
from app.models import ComparisonType, VisualationType


def comparison_factory(
    comparison_type: ComparisonType, sensitivity: int
) -> BaseComparer:
    match comparison_type:
        case ComparisonType.PIXEL:
            return PixelComparer(sensitivity=sensitivity)
        case ComparisonType.STRUCTUAL:
            return SSIMComparer(sensitivity=sensitivity)
        case _:
            raise ValueError("Invalid Comparer type requested")


def visualisation_factory(visualisation_type: VisualationType) -> BaseVisualiser:
    match visualisation_type:
        case VisualationType.HEATMAP:
            return HeatmapVisualiser()
        case VisualationType.CONTOUR:
            return ContourVisualiser()
        case _:
            raise ValueError("Invalid Visualiser type requested")
