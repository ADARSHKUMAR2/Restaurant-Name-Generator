# Use a lightweight Python 3.12 image
FROM python:3.12-slim

# Force Python to print logs immediately!
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system tools needed for database/kafka connections
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your actual code into the container
COPY . .