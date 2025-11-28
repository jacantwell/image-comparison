from typing import Annotated

from fastapi import Depends, Request

from app.database import BaseDatabase


async def get_db(request: Request) -> BaseDatabase:
    """Return database from app state"""
    return request.app.state.db


DatabaseDep = Annotated[BaseDatabase, Depends(get_db)]
