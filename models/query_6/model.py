from pydantic import BaseModel
from typing import Optional


class FindCities(BaseModel):
    cityId: int
    cityName: Optional[str] = None
    activeUserCount: int