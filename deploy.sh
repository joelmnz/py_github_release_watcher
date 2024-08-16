#!/bin/bash

# Example usage: ./deploy.sh 8080

# Define variables
APP_NAME="my_flask_app"
DOCKER_IMAGE_NAME="${APP_NAME}_image"  # Append "_image" to APP_NAME
DOCKER_CONTAINER_NAME="${APP_NAME}_container"  # Append "_container" to APP_NAME
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
docker run -d -p $PORT:5000 --name $DOCKER_CONTAINER_NAME -v $APP_DATA_VOLUME_NAME:/app_data $DOCKER_IMAGE_NAME

echo "Flask app is deployed and running at http://localhost:$PORT"
