# MAADBproject

This project requires a specific data setup and uses Docker for containerization. Please follow the instructions below to get it running.

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd MAADBproject
    ```

2.  **Create the Data Folder:**
    In the root of the project directory, create a folder named `data`:
    ```bash
    mkdir data
    ```

3.  **Copy Dataset Folders:**
    Copy the `dynamic` and `static` folders from your dataset into the newly created `data` folder. Your project structure should then look like this:
    ```
    MAADBproject/
    ├── data/
    │   ├── dynamic/
    │   └── static/
    ├── ... (other project files)
    ```
    Alternatively, if you prefer not to copy the folders, ensure that the correct paths to your `dynamic` and `static` dataset folders are properly configured within the project's configuration files.

## Running the Project with Docker

1.  **Build the Docker Image:**
    Navigate to the root of the project directory (where the `docker-compose.yml` file is located) and run the following command:
    ```bash
    docker-compose build app
    ```
    This command will build the Docker image for the application service.

2.  **Start the Docker Containers:**
    Once the image is built, start the containers in detached mode using the following command:
    ```bash
    docker-compose up -d
    ```
    This will start all the services defined in your `docker-compose.yml` file in the background.

## Waiting and Praying

After starting the containers, the application will begin its setup process. **Be patient.** The MongoDB setup can take a significant amount of time to complete.

## Monitoring the Setup

To monitor the progress, especially the MongoDB setup, you can periodically check the logs of the application container using the following command:

```bash
docker logs maadbproject-app-1
```

---


## 🔄 Restore Docker Volume Backups (Windows & macOS/Linux)

To restore the database volumes from backup, follow these steps:

### 1. 📥 Download Backup Files
Place the following `.tar.bz2` files in a folder of your choice:
- `mongodb_backup.tar.bz2`
- `neo4j_backup.tar.bz2`
- `postgres_backup.tar.bz2`

---

### 2. 📁 Open a Terminal in That Folder
- **Windows:** Right-click the folder and select **“Open in PowerShell”**
- **macOS/Linux:** Open Terminal and `cd` into the folder

---

### 3. 🗃️ Create Docker Volumes (if not already created)

```bash
docker volume create maadbproject_mongodb_data
docker volume create maadbproject_neo4j_data
docker volume create maadbproject_postgres_data
```

---

### 4. 🔧 Run Restore Commands

> ⚠️ Use `${PWD}` in **PowerShell**, and `$(pwd)` in **macOS/Linux Terminal**

#### ✅ Windows PowerShell
```powershell
docker run --rm -v maadbproject_mongodb_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore mongodb_backup.tar.bz2
docker run --rm -v maadbproject_neo4j_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore neo4j_backup.tar.bz2
docker run --rm -v maadbproject_postgres_data:/volume -v ${PWD}:/backup loomchild/volume-backup restore postgres_backup.tar.bz2
```

#### ✅ macOS/Linux Terminal
```bash
docker run --rm -v maadbproject_mongodb_data:/volume -v $(pwd):/backup loomchild/volume-backup restore mongodb_backup.tar.bz2
docker run --rm -v maadbproject_neo4j_data:/volume -v $(pwd):/backup loomchild/volume-backup restore neo4j_backup.tar.bz2
docker run --rm -v maadbproject_postgres_data:/volume -v $(pwd):/backup loomchild/volume-backup restore postgres_backup.tar.bz2
```

---

💡 If you encounter errors about missing files, ensure the `.tar.bz2` files are in the current folder and correctly named.


---
la collection Person su mongo nel campo email ha una serie di email separate da ; come un'unica stringa, runnare email_to_array.py per trasformare il campo in un array di stringhe
```bash
docker exec maadbproject-app-1 python /app/misch/email_to_array.py
```

---

## 🛠️ Create Indexes Manually After Initialization

After all containers are up and running and the data has been properly initialized, it's **highly recommended** to manually create a few indexes in each database engine to improve query performance, especially on large datasets.

### 🐘 PostgreSQL

Access your PostgreSQL client or connect via container and run the following SQL commands:

```sql
CREATE INDEX idx_organization_name ON organization(name);
CREATE INDEX idx_tag_class_id ON Tag("TypeTagClassId"); -- for Matteo
CREATE INDEX idx_place_id ON place(id); -- Added by Matteo
CREATE INDEX idx_tagclass_name ON tagclass(name); -- Added by Matteo
```

### 🍃 MongoDB

Enter the Mongo shell (`mongosh`) from within the container:

```bash
docker exec -it <mongo_container_name> mongosh
```

Then execute:

```javascript
db.person.createIndex({ email: 1 }, { name: "email_index" });
db.post.createIndex({ CreatorPersonId: 1 }, { name: "post_creator_index" });
db.person.createIndex({ LocationCityId: 1 }, { name: "location_city_index" });
db.Comment.createIndex({ CreatorPersonId: 1, ParentPostId: 1 });
```

### 🧠 Neo4j

Using the Neo4j browser or `cypher-shell`, execute the following Cypher query:

```cypher
CREATE INDEX works_from_date_index FOR ()-[r:WORK_AT]-() ON (r.workFrom);
```

> 🔍 These indexes are not created automatically to preserve full control over the schema. Creating them ensures **faster response times** for the most common and critical queries used in the project.
