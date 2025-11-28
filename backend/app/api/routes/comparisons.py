import base64
import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.api.deps import DatabaseDep
from app.lib import comparison_factory, visualisation_factory
from app.models import ComparisonType, VisualationType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comparisons")


@router.post("/")
async def compare(
    db: DatabaseDep,
    before_image: Annotated[UploadFile, File()],
    after_image: Annotated[UploadFile, File()],
    comparison_type: Annotated[ComparisonType, Form()],
    visualtion_type: Annotated[VisualationType, Form()],
    sensitivity: Annotated[int, Form()],
) -> str:
    """
    Compare two images and return a unique comparison ID.

    Args:
        db: Database dependency
        before_image: The first image to compare
        after_image: The second image to compare
        comparison_type: The type of comparison to perform
        visualtion_type: The type of visualisation to generate
        sensitivity: Sensitivity level for the comparison

    Returns:
        Unique id for the comparison result
    """
    # Validate sensitivity range
    if not 0 <= sensitivity <= 100:
        raise HTTPException(
            status_code=400, detail="Sensitivity must be between 0 and 100"
        )

    # Initialise tools
    try:
        comparer = comparison_factory(comparison_type, sensitivity)
        visualiser = visualisation_factory(visualtion_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to initialise comparison tools: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to initialise comparison tools"
        )

    # Read image bytes from uploaded files
    try:
        before_bytes = await before_image.read()
        after_bytes = await after_image.read()
    except Exception as e:
        logger.error(f"Failed to read image files: {e}")
        raise HTTPException(status_code=400, detail="Failed to read uploaded images")

    # Validate image data
    if not before_bytes or not after_bytes:
        raise HTTPException(status_code=400, detail="Uploaded images cannot be empty")

    # Run the comparison
    try:
        comparison = comparer.compare(before_bytes, after_bytes)
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to compare images")

    # Add visualisation to comparison result
    try:
        comparison.visualisation = visualiser.visualise(
            before_bytes, after_bytes, comparison
        )
    except Exception as e:
        logger.error(f"Visualisation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate visualisation")

    # Save the result in the db
    try:
        result_id = await db.create(comparison)
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save comparison result")

    return result_id


@router.get("/comparison_types")
def get_comparison_types() -> list[str]:
    """
    Get list of available comparison types.

    Returns:
        List of comparison type names
    """
    try:
        return ComparisonType.to_list()
    except Exception as e:
        logger.error(f"Failed to retrieve comparison types: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve comparison types"
        )


@router.get("/visualisation_types")
def get_visualisation_types() -> list[str]:
    """
    Get list of available visualisation types.

    Returns:
        List of visualisation type names
    """
    try:
        return VisualationType.to_list()
    except Exception as e:
        logger.error(f"Failed to retrieve visualisation types: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve visualisation types"
        )


@router.get("/")
async def get_comparisons(db: DatabaseDep) -> list[str]:
    """
    Get list of all comparison IDs.

    Args:
        db: Database dependency

    Returns:
        List of comparison ids
    """
    try:
        ids = await db.read_all()
        return ids
    except Exception as e:
        logger.error(f"Failed to retrieve comparisons: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparisons")


@router.get("/{id}")
async def get_comparison(db: DatabaseDep, id: str) -> JSONResponse:
    """
    Get a specific comparison result by ID.

    Args:
        db: Database dependency
        id: Unique id of the comparison

    Returns:
        JSON response with comparison score and encoded visualisation
    """
    # Validate ID format
    if not id or not id.strip():
        raise HTTPException(status_code=400, detail="Comparison ID cannot be empty")

    # Retrieve comparison from database
    try:
        comparison = await db.read(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TypeError as e:
        logger.error(f"Invalid ID type: {e}")
        raise HTTPException(status_code=400, detail="Invalid comparison ID format")
    except Exception as e:
        logger.error(f"Database error retrieving comparison {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve comparison")

    # Validate visualisation exists
    if not comparison.visualisation:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate visualisation for comparison, please try again.",
        )

    # Encode visualisation
    try:
        base64_image = base64.b64encode(comparison.visualisation).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encode visualisation for comparison {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to process visualisation")

    # Build and return response
    try:
        return JSONResponse(
            {
                "score": comparison.score,
                "image_data": f"data:image/png;base64,{base64_image}",
            }
        )
    except Exception as e:
        logger.error(f"Failed to build response for comparison {id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to build response")
