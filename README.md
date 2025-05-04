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