from pydantic import BaseModel, field_serializer,ConfigDict, Field
from datetime import datetime
from typing import Optional

class FindForumResponse(BaseModel):
    id: int
    title: Optional[str] = None
    creationDate: Optional[datetime]
    ModeratorPersonId: int
    interested_members: int
    model_config = ConfigDict(arbitrary_types_allowed=True) # abilita tipi non standard -> datetime
    @field_serializer("creationDate")
    def format_creation_date(self, dt: Optional[datetime], _info):
        if dt:
            return dt.strftime("%d/%m/%Y %H:%M")
        return None