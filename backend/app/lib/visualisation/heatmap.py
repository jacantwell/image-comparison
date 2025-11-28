import logging

import cv2
import numpy as np

from app.models import ComparisonResult

from .base import BaseVisualiser

logger = logging.getLogger(__name__)


class HeatmapVisualisationError(Exception):
    """Raised when heatmap visualisation fails."""

    pass


class HeatmapVisualiser(BaseVisualiser):
    """Shows differences as a color heatmap overlay.

    Best for: Showing intensity/magnitude of changes
    """

    def __init__(
        self, colormap: int = cv2.COLORMAP_JET, opacity: float = 0.5, **kwargs
    ):
        """Initialize heatmap visualiser.

        Args:
            colormap: OpenCV colormap constant (COLORMAP_JET, COLORMAP_HOT, etc.)
            opacity: Opacity of heatmap overlay (0.0-1.0). 0 is transparent, 1 is opaque.
        """
        self.colormap = colormap
        self.opacity = opacity

    def _load_images(self, img1: bytes, img2: bytes) -> tuple[np.ndarray, np.ndarray]:
        """Load images from bytes to numpy arrays."""

        try:
            img1_array = cv2.imdecode(np.frombuffer(img1, np.uint8), cv2.IMREAD_COLOR)
            img2_array = cv2.imdecode(np.frombuffer(img2, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Failed to decode images: {e}")
            raise HeatmapVisualisationError(f"Image decoding failed: {e}") from e

        if img1_array is None:
            logger.error("Failed to decode first image")
            raise HeatmapVisualisationError("Failed to decode first image")

        if img2_array is None:
            logger.error("Failed to decode second image")
            raise HeatmapVisualisationError("Failed to decode second image")

        return img1_array, img2_array

    def _create_heatmap(self, difference_map: np.ndarray) -> np.ndarray:
        """Create colored heatmap from difference map.

        Args:
            difference_map: Grayscale difference map.

        Returns:
            Colored heatmap as BGR image.
        """
        try:
            # Create output array with correct dtype
            normalised = np.zeros_like(difference_map, dtype=np.uint8)

            # Normalize to 0-255 range
            cv2.normalize(difference_map, normalised, 0, 255, cv2.NORM_MINMAX)

            # Apply colormap
            heatmap = cv2.applyColorMap(normalised, self.colormap)

            return heatmap

        except cv2.error as e:
            logger.error(f"OpenCV heatmap creation failed: {e}")
            raise HeatmapVisualisationError(f"Heatmap creation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during heatmap creation: {e}")
            raise HeatmapVisualisationError(f"Unexpected heatmap error: {e}") from e

    def _blend_heatmap(self, base_image: np.ndarray, heatmap: np.ndarray) -> np.ndarray:
        """Blend heatmap with base image.

        Args:
            base_image: Base image to overlay on.
            heatmap: Colored heatmap to blend.

        Returns:
            Blended result image.
        """
        try:
            # Ensure base image is in the right format for blending (3 channels)
            if len(base_image.shape) == 2:  # If grayscale
                img_color = cv2.cvtColor(base_image, cv2.COLOR_GRAY2BGR)
            else:
                img_color = base_image

            # Blend with original
            result = cv2.addWeighted(
                img_color, 1 - self.opacity, heatmap, self.opacity, 0
            )

            return result

        except cv2.error as e:
            logger.error(f"OpenCV blending failed: {e}")
            raise HeatmapVisualisationError(f"Heatmap blending failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during blending: {e}")
            raise HeatmapVisualisationError(f"Unexpected blending error: {e}") from e

    def visualise(
        self, img1: bytes, img2: bytes, comparison: ComparisonResult
    ) -> bytes:
        """Create heatmap visualisation of image differences.

        This method creates a colored heatmap overlay showing the intensity
        of differences between two images.

        Args:
            img1: First image as bytes (not directly used, kept for interface compatibility).
            img2: Second image as bytes (used as base for overlay).
            comparison: Comparison result containing difference map.

        Returns:
            PNG-encoded visualisation as bytes.

        Raises:
            HeatmapVisualisationError: If visualisation fails at any stage.
        """
        try:
            # Create heatmap from difference map
            heatmap = self._create_heatmap(comparison.map)

            # Load base image
            _, img2_array = self._load_images(img1, img2)

            # Blend heatmap with base image
            result = self._blend_heatmap(img2_array, heatmap)

            # Encode result
            success, encoded = cv2.imencode(".png", result)

            if not success or encoded is None:
                raise HeatmapVisualisationError("Failed to encode result image to PNG")

            return encoded.tobytes()

        except HeatmapVisualisationError:
            raise
        except cv2.error as e:
            logger.error(f"OpenCV imencode failed: {e}")
            raise HeatmapVisualisationError(f"Image encoding failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in visualise: {e}")
            raise HeatmapVisualisationError(f"Visualisation failed: {e}") from e
