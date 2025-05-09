from pydantic import BaseModel, field_validator
from typing import Optional, List, Any
import math  # Required if checking for float NaN


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
    imageFile: Optional[float] = None  # Assuming this is what was intended

    # Pydantic V2 style validator
    @field_validator('content', 'browserUsed', 'language', 'locationIP', mode='before')
    @classmethod  # Important: field_validator expects a classmethod
    def handle_nan_values(cls, value: Any) -> Optional[str]:
        # Check for float NaN
        if isinstance(value, float) and math.isnan(value):
            return None  # Or return "" if an empty string is preferred

        # Optionally, check for string "NaN" or "nan" if that might occur
        if isinstance(value, str) and value.lower() == 'nan':
            return None  # Or return ""

        return value

    class Config:
        # For Pydantic V1, orm_mode = True
        # For Pydantic V2, use model_config
        model_config = {
            "from_attributes": True,  # Equivalent to orm_mode = True
            "populate_by_name": True  # Equivalent to allow_population_by_field_name = True
        }


class PostResponse(PostBase):
    pass


class PersonBase(BaseModel):
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

    # You might want a similar validator here if these fields can also receive NaN
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