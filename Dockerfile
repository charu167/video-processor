# Use the official Python Alpine image as the base
FROM python:3.9-alpine

# Install FFmpeg and other dependencies using apk
RUN apk add --no-cache ffmpeg

# Set the working directory
WORKDIR /processor

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the command to run the application
CMD ["python3", "main.py"]