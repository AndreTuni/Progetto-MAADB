from pydantic import BaseModel, Field
from typing import Optional, List

# This model can represent the structure of a post document in MongoDB
# We might not use all fields for every response, but it's good to have a full model
class PostBase(BaseModel):
    ContainerForumId: Optional[int] = None
    CreatorPersonId: int
    LocationCountryId: Optional[int] = None
    browserUsed: Optional[str] = None
    content: Optional[str] = None
    creationDate: str
    id: int # This is your custom Int64 ID
    language: Optional[str] = None # Still a string as per your example document "pl;en"
    length: Optional[int] = None
    locationIP: Optional[str] = None
    imageFile: Optional[float] = None # Assuming this is what was intended, though String for URL/path is more common

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        # If your MongoDB uses "_id" and you want to map it to a field named "mongo_id" for example:
        # fields = {'mongo_id': '_id'} # Pydantic v1 style
        # For Pydantic v2, you might use alias_generator or field_serializer for _id if needed,
        # but FastAPI handles ObjectId conversion well.

class PostResponse(PostBase):
    # You can add or exclude fields specifically for the response
    pass

class PersonBase(BaseModel):
    LocationCityId: Optional[int] = None
    birthday: Optional[str] = None
    creationDate: str
    # --- MODIFIED FIELD ---
    email: List[str] # Changed from str to List[str]
    # --- END MODIFIED FIELD ---
    id: int # This is your custom Int32 ID
    language: Optional[str] = None # Still a string as per your example document "pl;en"
    lastName: str
    locationIP: Optional[str] = None
    browserUsed: Optional[str] = None
    firstName: str
    gender: Optional[str] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

# You might also want a PersonResponse model if you intend to return Person objects
# from an endpoint, though your current query returns Post objects.
# class PersonResponse(PersonBase):
#     pass