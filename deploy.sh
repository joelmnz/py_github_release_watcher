#!/bin/bash

# Example usage: ./deploy.sh 8080

# Check if the PORT argument is supplied
if [ -z "$1" ]; then
    echo "Error: You must specify a PORT."
    echo "Usage: $0 <port>"
    exit 1
fi

# Define variables
APP_NAME="py_github_release_watcher"
DOCKER_IMAGE_NAME="${APP_NAME}_image"
DOCKER_CONTAINER_NAME="${APP_NAME}"
APP_DATA_VOLUME_NAME="${APP_NAME}_data"  # Volume name for app data
PORT=${1:-5000}  # Use the first argument as the port, default to 5000 if not provided

# Create the Docker volume if it doesn't exist
if [ -z "$(docker volume ls -q -f name=$APP_DATA_VOLUME_NAME)" ]; then
    echo "Creating Docker volume: $APP_DATA_VOLUME_NAME"
    docker volume create $APP_DATA_VOLUME_NAME
fi

# Build the Docker image
echo "Building the Docker image..."
docker build -t $DOCKER_IMAGE_NAME .

# Stop and remove any existing container
if [ "$(docker ps -aq -f name=$DOCKER_CONTAINER_NAME)" ]; then
    echo "Stopping and removing existing container..."
    docker stop $DOCKER_CONTAINER_NAME
    docker rm $DOCKER_CONTAINER_NAME
fi

# Run the Docker container with volume mapping
echo "Running the Docker container on port $PORT..."
#docker run -d -p $PORT:5000 --name $DOCKER_CONTAINER_NAME -v $APP_DATA_VOLUME_NAME:/app_data $DOCKER_IMAGE_NAME
docker run -d -p $PORT:5000 --name $DOCKER_CONTAINER_NAME -v $APP_DATA_VOLUME_NAME:/app_data -e CACHE_DIR=/app_data $DOCKER_IMAGE_NAME

echo "App deployed and running at http://localhost:$PORT"
