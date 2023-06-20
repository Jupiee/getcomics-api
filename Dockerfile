FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy source code to container
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Expose port 80 (FastAPI default)
EXPOSE 80

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]