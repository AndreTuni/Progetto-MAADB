#POSTGRES

### Table: organization
| Column           | Data Type | Description                               |
| ---------------- | --------- | ----------------------------------------- |
| id               | integer   | Primary Key                               |
| type             | text      |                                           |
| name             | text      |                                           |
| url              | text      |                                           |
| LocationPlaceId  | integer   | Foreign Key to `place` table             |

**Keys:**
* Primary Key: `organization_pkey` (id)

**Foreign Keys:**
* `organization_LocationPlaceId_fkey` (LocationPlaceId) -> `place` (id)
**Indexes:**
* `iu_organization_pkey` (id) UNIQUE


### Table: place
| Column         | Data Type | Description                              |
| -------------- | --------- | ---------------------------------------- |
| id             | integer   | Primary Key                              |
| name           | text      |                                          |
| url            | text      |                                          |
| type           | text      |                                          |
| PartOfPlaceId  | integer   | Foreign Key to `place` table (self-reference) |

**Keys:**
* Primary Key: `place_pkey` (id)
**Foreign Keys:**
* `place_PartOfPlaceId_fkey` (PartOfPlaceId) -> `place` (id)

**Indexes:**
* `iu_place_pkey` (id) UNIQUE


### Table: tag
| Column         | Data Type | Description                              |
| -------------- | --------- | ---------------------------------------- |
| id             | integer   | Primary Key                              |
| name           | text      |                                          |
| url            | text      |                                          |
| TypeTagClassId | integer   | Foreign Key to `tagclass` table             |
<br>
**Keys:**
* Primary Key: `tag_pkey` (id)

**Foreign Keys:**
* `tag_TypeTagClassId_fkey` (TypeTagClassId) -> `tagclass` (id)

**Indexes:**
* `iu_tag_pkey` (id) UNIQUE


### Table: tagclass
| Column              | Data Type | Description                                      |
| ------------------- | --------- | ------------------------------------------------ |
| id                  | integer   | Primary Key                                      |
| name                | text      |                                                  |
| url                 | text      |                                                  |
| SubclassOfTagClassId | integer  | Foreign Key to `tagclass` table (self-reference) |

**Keys:**
* Primary Key: `tagclass_pkey` (id)

**Foreign Keys:**
* `tagclass_SubclassOfTagClassId_fkey` (SubclassOfTagClassId) -> `tagclass` (id)

**Indexes:**
* `iu_tagclass_pkey` (id) UNIQUE
