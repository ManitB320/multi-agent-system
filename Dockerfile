# Dockerfile
# Use a slim Python image for a smaller final size
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# The GOOGLE_API_KEY will be securely set via Render's dashboard environment variables.
ENV GOOGLE_API_KEY="" 

# Install necessary system dependencies for PyMuPDF (fitz) and FAISS
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \x
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirement files first to leverage Docker caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Create necessary directories and set permissions
RUN mkdir -p /app/pdfs /app/pdf_store /app/logs
# Grant write permissions for FAISS data and logs
RUN chmod -R 777 /app/pdf_store
RUN chmod -R 777 /app/logs

# Expose the port (Render will use this)
EXPOSE 8000

# Command to run the application using uvicorn, reading the port from Render's environment
# Use sh -c to execute the command inside a shell
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]