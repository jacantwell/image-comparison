import logging

import cv2
import numpy as np

from app.models import ComparisonResult

from .base import BaseComparer

logger = logging.getLogger(__name__)


class PixelComparisonError(Exception):
    """Raised when pixel comparison fails."""

    pass


class PixelComparer(BaseComparer):
    """Simple pixel-by-pixel comparison.

    Best for: Fast comparison, exact pixel matching
    Pros: Very fast, simple to understand
    Cons: Sensitive to minor variations, compression artifacts
    """

    def __init__(self, sensitivity: int = 30):
        """Initialize pixel comparer.

        Args:
            sensitivity: How strict the comparison is (0-100).
                        100 = Strict (detects 1-value changes).
                        0 = Loose (ignores almost everything).
        """
        super().__init__(sensitivity=sensitivity)

    def _load_images(self, img1: bytes, img2: bytes) -> tuple[np.ndarray, np.ndarray]:
        """Load images from bytes to numpy arrays."""

        try:
            img1_array = cv2.imdecode(np.frombuffer(img1, np.uint8), cv2.IMREAD_COLOR)
            img2_array = cv2.imdecode(np.frombuffer(img2, np.uint8), cv2.IMREAD_COLOR)
        except Exception as e:
            logger.error(f"Failed to decode images: {e}")
            raise PixelComparisonError(f"Image decoding failed: {e}") from e

        if img1_array is None:
            logger.error("Failed to decode first image")
            raise PixelComparisonError("Failed to decode first image")

        if img2_array is None:
            logger.error("Failed to decode second image")
            raise PixelComparisonError("Failed to decode second image")

        return img1_array, img2_array

    def _compute_difference_maps(
        self, img1_array: np.ndarray, img2_array: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Compute grayscale and binary difference maps.

        Args:
            img1_array: First image as numpy array.
            img2_array: Second image as numpy array.

        Returns:
            Tuple of (gray_diff, binary_diff) maps.
        """
        try:
            # Compute absolute difference
            abs_diff = cv2.absdiff(img1_array, img2_array)

            # Convert to grayscale
            gray_diff = cv2.cvtColor(abs_diff, cv2.COLOR_BGR2GRAY)

            # Convert sensitivity to threshold value
            threshold_value = int(255 * (1 - (self.sensitivity / 100)))

            # Apply threshold to create binary map
            _, binary_diff = cv2.threshold(
                gray_diff, threshold_value, 255, cv2.THRESH_BINARY
            )

            return gray_diff, binary_diff

        except cv2.error as e:
            logger.error(f"OpenCV difference computation failed: {e}")
            raise PixelComparisonError(f"Difference computation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during difference computation: {e}")
            raise PixelComparisonError(f"Unexpected comparison error: {e}") from e

    def _calculate_score(self, binary_diff: np.ndarray) -> float:
        """Calculate difference score as percentage of changed pixels.

        Args:
            binary_diff: Binary difference map.

        Returns:
            Difference score as percentage (0-100).
        """
        try:
            total_pixels = binary_diff.size
            changed_pixels = np.count_nonzero(binary_diff)
            difference_score = (changed_pixels / total_pixels) * 100

            logger.debug(
                f"Pixel comparison: {changed_pixels}/{total_pixels} pixels changed "
                f"({difference_score:.2f}%)"
            )

            return difference_score

        except Exception as e:
            logger.error(f"Failed to calculate difference score: {e}")
            raise PixelComparisonError(f"Score calculation failed: {e}") from e

    def compare(self, img1: bytes, img2: bytes) -> ComparisonResult:
        """Compare images using absolute pixel differences.

        This method performs pixel-by-pixel comparison, computing the absolute
        difference between corresponding pixels and applying a sensitivity threshold.

        Args:
            img1: First image as bytes.
            img2: Second image as bytes.

        Returns:
            ComparisonResult containing score and difference map.

        Raises:
            PixelComparisonError: If comparison fails at any stage.
        """
        try:
            # Load images
            img1_array, img2_array = self._load_images(img1, img2)

            # Validate dimensions match
            if img1_array.shape != img2_array.shape:
                raise PixelComparisonError(
                    f"Image shapes must match: {img1_array.shape} vs {img2_array.shape}"
                )

            # Compute difference maps
            gray_diff, binary_diff = self._compute_difference_maps(
                img1_array, img2_array
            )

            # Calculate difference score
            difference_score = self._calculate_score(binary_diff)

            return ComparisonResult(score=difference_score, map=gray_diff)

        except PixelComparisonError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compare: {e}")
            raise PixelComparisonError(f"Comparison failed: {e}") from e
