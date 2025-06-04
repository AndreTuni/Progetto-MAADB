from pydantic import BaseModel, field_serializer,ConfigDict, Field
from datetime import datetime
from typing import Optional


class ForumResponse(BaseModel):
    forum_id: int
    title: str
    creation_date: Optional[datetime] = Field(alias="membership_creation_date")
    member_count : int
    model_config = ConfigDict(arbitrary_types_allowed=True) # abilita tipi non standard -> datetime
    @field_serializer("creation_date")
    def format_creation_date(self, dt: Optional[datetime], _info):
        if dt:
            return dt.strftime("%d/%m/%Y %H:%M")
        return None