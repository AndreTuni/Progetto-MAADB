from pydantic import BaseModel
from typing import List, Optional


class TagUsage(BaseModel):
    tag_name: str
    count: int
    tag_url: Optional[str] = None
    tag_class_name: Optional[str] = None


class MostUsedTagsResponse(BaseModel):
    user_email: str
    city_name: Optional[str] = None
    tags: List[TagUsage]
    message: Optional[str] = None