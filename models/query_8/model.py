from pydantic import BaseModel
from typing import Optional

class TagResponse(BaseModel):
    tag_id: int
    tag_name: str
    tag_url: Optional[str]
    class_id: int
    class_name: str
    class_url: Optional[str]
    usage_count: int