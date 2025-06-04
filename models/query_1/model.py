from pydantic import BaseModel


class PostResponse(BaseModel):  # Placeholder
    id: int
    content: str | None = None
    creationDate: str
    CreatorPersonId: int