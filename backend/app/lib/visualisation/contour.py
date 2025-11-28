import logging

import cv2
import numpy as np

from app.models import ComparisonResult

from .base import BaseVisualiser

logger = logging.getLogger(__name__)


class ContourVisualisationError(Exception):
    """Raised when contour visualisation fails."""

    pass


class ContourVisualiser(BaseVisualiser):
    """Highlights differences using contours and bounding boxes.

    This visualiser creates a professional-looking overlay that highlights
    differences between two images using filled contours and bounding boxes.
    """

    def __init__(
        self,
        min_contour_area: int = 40,
        highlight_color: tuple[int, int, int] = (0, 255, 0),
        box_thickness: int = 2,
        fill_opacity: float = 0.3,
        **kwargs,
    ):
        """Initialize contour visualiser.

        Args:
            min_contour_area: Minimum contour area in pixels to draw (filters noise).
                Must be non-negative.
            highlight_color: BGR color tuple for highlights (0-255 for each channel).
            box_thickness: Thickness of bounding boxes in pixels. Must be positive.
            fill_opacity: Opacity of filled contours (0.0-1.0). 0 is transparent, 1 is opaque.
        """

        self.min_contour_area = min_contour_area
        self.highlight_color = highlight_color
        self.box_thickness = box_thickness
        self.fill_opacity = fill_opacity

    def _load_images(self, img1: bytes, img2: bytes) -> tuple[np.ndarray, np.ndarray]:
        """Load images from bytes to numpy arrays."""

        try:
            img1_array = cv2.imdecode(np.frombuffer(img1, np.uint8), cv2.IMREAD_COLOR)
            img2_array = cv2.imdecode(np.frombuffer(img2, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Failed to decode images: {e}")
            raise ContourVisualisationError(f"Image decoding failed: {e}") from e

        if img1_array is None:
            logger.error(f"Failed to decode first image")
            raise ContourVisualisationError("Failed to decode first image")

        if img2_array is None:
            logger.error(f"Failed to decode second image")
            raise ContourVisualisationError("Failed to decode second image")

        return img1_array, img2_array

    def _find_significant_contours(
        self, difference_map: np.ndarray
    ) -> list[np.ndarray]:
        """Find and filter contours from difference map.

        Args:
            difference_map: Grayscale difference map.

        Returns:
            List of contours that meet the minimum area threshold.
        """
        try:
            contours, _ = cv2.findContours(
                difference_map, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
        except cv2.error as e:
            logger.error(f"OpenCV findContours failed: {e}")
            raise ContourVisualisationError(f"Contour detection failed: {e}") from e

        significant_contours = [
            c for c in contours if cv2.contourArea(c) > self.min_contour_area
        ]

        logger.debug(
            f"Found {len(contours)} contours, {len(significant_contours)} above "
            f"minimum area {self.min_contour_area}"
        )

        return significant_contours

    def _create_overlay(
        self, base_image: np.ndarray, contours: list[np.ndarray]
    ) -> np.ndarray:
        """Create overlay with filled contours and bounding boxes.

        Args:
            base_image: Base image to overlay on.
            contours: List of contours to draw.

        Returns:
            Image with overlay applied.
        """
        try:
            result = base_image.copy()
            overlay = base_image.copy()

            # Draw filled contours on overlay
            for contour in contours:
                cv2.drawContours(overlay, [contour], -1, self.highlight_color, -1)

            # Blend overlay with base image
            result = cv2.addWeighted(
                result, 1 - self.fill_opacity, overlay, self.fill_opacity, 0
            )

            # Draw bounding boxes
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(
                    result,
                    (x, y),
                    (x + w, y + h),
                    self.highlight_color,
                    self.box_thickness,
                )

            return result

        except cv2.error as e:
            logger.error(f"OpenCV overlay creation failed: {e}")
            raise ContourVisualisationError(f"Overlay creation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during overlay creation: {e}")
            raise ContourVisualisationError(f"Unexpected overlay error: {e}") from e

    def visualise(
        self, img1: bytes, img2: bytes, comparison: ComparisonResult
    ) -> bytes:
        """Create contour-based visualisation of image differences.

        This method creates a professional-looking overlay highlighting differences
        between two images using filled contours and bounding boxes.

        Args:
            img1: First image as bytes (not directly used, kept for interface compatibility).
            img2: Second image as bytes (used as base for overlay).
            comparison: Comparison result containing difference maps.

        Returns:
            PNG-encoded visualisation as bytes.

        Raises:
            ContourVisualisationError: If visualisation fails at any stage.
        """
        try:
            # Find significant contours
            significant_contours = self._find_significant_contours(comparison.map)

            if not significant_contours:
                logger.info("No significant differences found")

            # Load images
            _, img2_array = self._load_images(img1, img2)

            # Create overlay
            result = self._create_overlay(img2_array, significant_contours)

            # Encode and return
            success, encoded = cv2.imencode(".png", result)

            if not success or encoded is None:
                raise ContourVisualisationError("Failed to encode result image to PNG")

            return encoded.tobytes()
        except ContourVisualisationError:
            raise
        except cv2.error as e:
            logger.error(f"OpenCV imencode failed: {e}")
            raise ContourVisualisationError(f"Image encoding failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in visualise: {e}")
            raise ContourVisualisationError(f"Visualisation failed: {e}") from e
