# Use a slim Python 3.12 image for a smaller footprint
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code AND the shared directory
COPY backend/ ./backend
COPY shared/ ./shared

# Ensure the app can find the shared module
ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
