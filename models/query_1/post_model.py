# models/post_model.py

from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
import math

class PostBase(BaseModel):
    ContainerForumId: Optional[int] = None
    CreatorPersonId: int
    LocationCountryId: Optional[int] = None
    browserUsed: Optional[str] = None
    content: Optional[str] = None
    creationDate: str
    id: int  # This is your custom Int64 ID
    language: Optional[str] = None
    length: Optional[int] = None
    locationIP: Optional[str] = None
    imageFile: Optional[str] = None  # MODIFIED: Changed from Optional[float] to Optional[str]

    @field_validator('content', 'browserUsed', 'language', 'locationIP', 'imageFile', mode='before') # ADDED: 'imageFile'
    @classmethod
    def handle_nan_values(cls, value: Any) -> Optional[str]:
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, str) and value.lower() == 'nan':
            return None
        return value

    class Config:
        model_config = {
            "from_attributes": True,
            "populate_by_name": True
        }

class PostResponse(PostBase):
    pass

class PersonBase(BaseModel): # No changes needed here for this request
    LocationCityId: Optional[int] = None
    birthday: Optional[str] = None
    creationDate: str
    email: List[str]
    id: int
    language: Optional[str] = None
    lastName: str
    locationIP: Optional[str] = None
    browserUsed: Optional[str] = None
    firstName: str
    gender: Optional[str] = None

    @field_validator('language', 'locationIP', 'browserUsed', 'gender', 'birthday', mode='before')
    @classmethod
    def handle_person_nan_values(cls, value: Any) -> Optional[str]:
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, str) and value.lower() == 'nan':
            return None
        return value

    class Config:
        model_config = {
            "from_attributes": True,
            "populate_by_name": True
        }