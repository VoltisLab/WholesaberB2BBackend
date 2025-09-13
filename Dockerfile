FROM python:3.10 AS base

# Install system dependencies first
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    lsb-release

# Set environment variables separately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip && \
    pip3 install --timeout=500 --retries=5 --no-cache-dir -r requirements.txt


EXPOSE 8001


