import logging

import cv2
import numpy as np
from cv2.typing import MatLike
from skimage.metrics import structural_similarity as ssim

from app.models import ComparisonResult

from .base import BaseComparer

logger = logging.getLogger(__name__)


class SSIMComparisonError(Exception):
    """Raised when SSIM comparison fails."""

    pass


class SSIMComparer(BaseComparer):
    """Structural Similarity Comparer.

    Best for: Detecting human-perceptible changes (layout shifts, element changes).
    Pros: Ignores minor noise and lighting changes.
    Cons: Slower than pixel comparison.
    """

    def __init__(self, sensitivity: int = 80):
        """Initialize SSIM comparer.

        Args:
            sensitivity: How strict the comparison is (0-100).
                        Acts as a threshold for the binary mask.
        """
        super().__init__(sensitivity=sensitivity)

    def _load_images(self, img1: bytes, img2: bytes) -> tuple[MatLike, MatLike]:
        """Load images from bytes to grayscale numpy arrays."""

        try:
            img1_array = cv2.imdecode(
                np.frombuffer(img1, np.uint8), cv2.IMREAD_GRAYSCALE
            )
            img2_array = cv2.imdecode(
                np.frombuffer(img2, np.uint8), cv2.IMREAD_GRAYSCALE
            )
        except Exception as e:
            logger.error(f"Failed to decode images: {e}")
            raise SSIMComparisonError(f"Image decoding failed: {e}") from e

        if img1_array is None:
            logger.error("Failed to decode first image")
            raise SSIMComparisonError("Failed to decode first image")

        if img2_array is None:
            logger.error("Failed to decode second image")
            raise SSIMComparisonError("Failed to decode second image")

        return img1_array, img2_array

    def _compute_ssim(
        self, img1_gray: np.ndarray, img2_gray: np.ndarray
    ) -> tuple[float, np.ndarray]:
        """Compute SSIM score and difference map.

        Args:
            img1_gray: First grayscale image.
            img2_gray: Second grayscale image.

        Returns:
            Tuple of (difference_score, difference_map).
        """
        try:
            # Compute SSIM with full difference map
            score, diff_map = ssim(img1_gray, img2_gray, full=True)  # type: ignore

            logger.debug(f"SSIM score: {score:.4f}")

            difference_score = (1 - score) * 100

            return difference_score, diff_map

        except Exception as e:
            logger.error(f"SSIM computation failed: {e}")
            raise SSIMComparisonError(f"SSIM computation failed: {e}") from e

    def _process_difference_map(self, diff_map: np.ndarray) -> np.ndarray:
        """Process SSIM difference map for visualization.

        SSIM diff_map ranges from -1 to 1 (1 being identical).
        Convert to 0-255 where 255 represents maximum difference.

        Args:
            diff_map: Raw SSIM difference map.

        Returns:
            Processed difference map as uint8 (0-255).
        """
        try:
            # Invert: 1 (identical) -> 0, -1 (different) -> 255
            inverted = (1 - diff_map) * 255

            # Convert to uint8 for OpenCV compatibility
            processed = inverted.astype(np.uint8)

            return processed

        except Exception as e:
            logger.error(f"Failed to process difference map: {e}")
            raise SSIMComparisonError(f"Difference map processing failed: {e}") from e

    def _apply_sensitivity_threshold(self, diff_map: np.ndarray) -> np.ndarray:
        """Apply sensitivity threshold to create binary difference map.

        Args:
            diff_map: Processed difference map (0-255).

        Returns:
            Binary difference map.
        """
        try:
            # Convert sensitivity to threshold value
            # If sensitivity is 80%, ignore the bottom 20% of noise
            threshold_val = int(255 * (1 - (self.sensitivity / 100)))

            _, binary_diff = cv2.threshold(
                diff_map, threshold_val, 255, cv2.THRESH_BINARY
            )

            return binary_diff

        except cv2.error as e:
            logger.error(f"OpenCV threshold failed: {e}")
            raise SSIMComparisonError(f"Threshold application failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error during thresholding: {e}")
            raise SSIMComparisonError(f"Unexpected threshold error: {e}") from e

    def compare(self, img1: bytes, img2: bytes) -> ComparisonResult:
        """Compare images using Structural Similarity Index.

        This method uses SSIM to detect perceptually significant differences,
        which is more robust to minor noise and lighting changes than pixel comparison.

        Args:
            img1: First image as bytes.
            img2: Second image as bytes.

        Returns:
            ComparisonResult containing SSIM score and difference map.

        Raises:
            SSIMComparisonError: If comparison fails at any stage.
        """
        try:
            # Load images as grayscale (SSIM works best on luminance)
            img1_gray, img2_gray = self._load_images(img1, img2)

            # Validate dimensions match
            if img1_gray.shape != img2_gray.shape:
                raise SSIMComparisonError(
                    f"Image shapes must match: {img1_gray.shape} vs {img2_gray.shape}"
                )

            # Compute SSIM score and difference map
            difference_score, raw_diff_map = self._compute_ssim(img1_gray, img2_gray)

            # Process difference map for visualization
            diff_map = self._process_difference_map(raw_diff_map)

            # Apply sensitivity threshold (optional, for binary mask)
            _ = self._apply_sensitivity_threshold(diff_map)

            return ComparisonResult(score=difference_score, map=diff_map)

        except SSIMComparisonError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in compare: {e}")
            raise SSIMComparisonError(f"Comparison failed: {e}") from e
