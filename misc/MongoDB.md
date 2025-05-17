## MongoDB

### MongoDB Database Structure

#### Collections

---

### 1. `post` (Collection)
- `_id` (ObjectId)  
- `ContainerForumId` (Int32)  
- `CreatorPersonId` (Int32)  
- `LocationCountryId` (Int32)  
- `browserUsed` (String)  
- `content` (String)  
- `creationDate` (String)  
- `id` (Int64)  
- `language` (String)  
- `length` (Int32)  
- `locationIP` (String)  
- `imageFile` (String)  

---

### 2. `person` (Collection)
- `_id` (ObjectId)  
- `LocationCityId` (Int32)  
- `birthday` (String)  
- `creationDate` (String)  
- `email` (String[])  
- `id` (Int32)  
- `language` (String)  
- `lastName` (String)  
- `locationIP` (String)  
- `browserUsed` (String)  
- `firstName` (String)  
- `gender` (String)  

---

### 3. `comment` (Collection)
- `_id` (ObjectId)  
- `CreatorPersonId` (Int64)  
- `LocationCountryId` (Int32)  
- `ParentCommentId` (Double)  
- `browserUsed` (String)  
- `content` (String)  
- `creationDate` (String)  
- `id` (Int64)  
- `length` (Int32)  
- `locationIP` (String)  
- `ParentPostId` (Double)  

---

### 4. `forum` (Collection)
- `_id` (ObjectId)  
- `ModeratorPersonId` (Int32)  
- `creationDate` (String)  
- `id` (Int32)  
- `title` (String)  
