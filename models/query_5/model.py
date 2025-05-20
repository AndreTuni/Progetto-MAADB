from pydantic import BaseModel
from typing import Optional


class SecondDegreeCommentResponse(BaseModel):
    post_id: int
    post_content: Optional[str]
    second_person_name: str
    comment_content:Optional[str]