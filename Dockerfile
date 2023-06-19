# Base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy source code to container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Set execute permissions for the entrypoint script
RUN chmod +x /app/entrypoint.sh

# Expose the port specified by the $PORT environment variable
EXPOSE $PORT

# Set the entrypoint to run the script
ENTRYPOINT ["/app/entrypoint.sh"]
