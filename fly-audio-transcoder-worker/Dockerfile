# Start from the smallest Alpine image
FROM alpine:latest

# Update the package list and install curl, jq, and ffmpeg
RUN apk --no-cache add \
    curl \
    jq \
    ffmpeg

# Set the working directory
WORKDIR /app

# Copy start.sh from your project directory to the working directory of the Docker image
COPY start.sh /app/start.sh

# Command to run the application
# CMD ["sh", "/app/start.sh"]
CMD ["sh", "start.sh"]