# Base image
FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Set working directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# Start Bash shell
USER vscode

# Run some code
# CMD ["python", "./main.py"]