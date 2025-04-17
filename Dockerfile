# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app/app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "uvicorn[standard]"

# Copy application code
COPY app ./app

# Expose the port your app runs on
EXPOSE 8010

# Set environment variable for production
ENV PYTHONUNBUFFERED=1

# Start the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8010"]
