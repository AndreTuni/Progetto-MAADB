// KNOWS (Person)-[:KNOWS]->(Person)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/knows.csv' AS row
MATCH (p1:Person {id: toInteger(row.Person1Id)}),
(p2:Person {id: toInteger(row.Person2Id)})
MERGE (p1)-[:KNOWS {creationDate: datetime(row.creationDate)}]->(p2);

// LIKES_POST (Person)-[:LIKES]->(Post)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/likes_post.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(po:Post {id: toInteger(row.PostId)})
MERGE (p)-[:LIKES {creationDate: datetime(row.creationDate)}]->(po);

// LIKES_COMMENT (Person)-[:LIKES]->(Comment)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/likes_comment.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(c:Comment {id: toInteger(row.CommentId)})
MERGE (p)-[:LIKES {creationDate: datetime(row.creationDate)}]->(c);

// HAS_INTEREST (Person)-[:HAS_INTEREST]->(Tag)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/has_interest.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(t:Tag {id: toInteger(row.TagId)})
MERGE (p)-[:HAS_INTEREST {creationDate: datetime(row.creationDate)}]->(t);

// MEMBER_OF (Person)-[:MEMBER_OF]->(Forum)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/member_of.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(f:Forum {id: toInteger(row.ForumId)})
MERGE (p)-[:MEMBER_OF {creationDate: datetime(row.creationDate)}]->(f);

// FORUM_HAS_TAG (Forum)-[:HAS_TAG]->(Tag)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/forum_has_tag.csv' AS row
MATCH (f:Forum {id: toInteger(row.ForumId)}),
(t:Tag {id: toInteger(row.TagId)})
MERGE (f)-[:HAS_TAG {creationDate: datetime(row.creationDate)}]->(t);

// POST_HAS_TAG (Post)-[:HAS_TAG]->(Tag)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/post_has_tag.csv' AS row
MATCH (p:Post {id: toInteger(row.PostId)}),
(t:Tag {id: toInteger(row.TagId)})
MERGE (p)-[:HAS_TAG {creationDate: datetime(row.creationDate)}]->(t);

// COMMENT_HAS_TAG (Comment)-[:HAS_TAG]->(Tag)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/comment_has_tag.csv' AS row
MATCH (c:Comment {id: toInteger(row.CommentId)}),
(t:Tag {id: toInteger(row.TagId)})
MERGE (c)-[:HAS_TAG {creationDate: datetime(row.creationDate)}]->(t);

// STUDY_AT (Person)-[:STUDY_AT]->(University)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/study_at.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(u:University {id: toInteger(row.UniversityId)})
MERGE (p)-[:STUDY_AT {creationDate: datetime(row.creationDate), classYear: toInteger(row.classYear)}]->(u);

// WORK_AT (Person)-[:WORK_AT]->(Company)
USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///absolute/path/to/work_at.csv' AS row
MATCH (p:Person {id: toInteger(row.PersonId)}),
(c:Company {id: toInteger(row.CompanyId)})
MERGE (p)-[:WORK_AT {creationDate: datetime(row.creationDate), workFrom: toInteger(row.workFrom)}]->(c);
