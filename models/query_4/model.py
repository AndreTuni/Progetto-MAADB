from typing import List, Optional # Make sure to import List from typing
from pydantic import BaseModel

class MemberInfo(BaseModel):
    id: int                 # Corresponds to person.id
    firstName: str
    lastName: str
    email: List[str]        # From MongoDB person.email (String Array)

class GroupDetail(BaseModel):
    companyId: int          # Corresponds to company.id (from Neo4j) / organization.id (PostgreSQL)
    companyName: str        # Fetched from PostgreSQL
    forumId: int            # Corresponds to forum.id (from Neo4j) / forum.id (MongoDB)
                            # Considering forum.id can be large, Python's int handles it.
    forumTitle: str         # Fetched from MongoDB
    members: List[MemberInfo]

# The final response from the endpoint could be a list of these groups
# For example: app.get("/path", response_model=List[GroupDetail])