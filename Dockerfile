# Use a multi-platform compatible FFmpeg base image
FROM linuxserver/ffmpeg:4.4-cli-ls70

# Install Python and pip using apt
RUN apt update && \
    apt install -y python3 python3-pip && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /processor

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set the command to run the application
CMD ["python3", "main.py"]