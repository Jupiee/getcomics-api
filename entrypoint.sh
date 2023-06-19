#!/bin/bash

# Start the FastAPI server with the port specified by the $PORT environment variable
exec uvicorn main:app --host 0.0.0.0 --port $PORT
