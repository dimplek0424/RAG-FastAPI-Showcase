# Use Python 3.10 (avoid 3.13 issue)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend folder contents
COPY ./backend /app

# Install system dependencies (optional, based on your packages)
RUN apt-get update && apt-get install -y build-essential cargo && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose the port your app runs on
EXPOSE 10000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=10000"]
