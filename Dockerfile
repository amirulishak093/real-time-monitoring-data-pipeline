# Base image
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the current directory to the working directory in the container
COPY ./sensor-data /app

# Install system dependencies
RUN apk add --no-cache build-base

# Install virtual environment
RUN python -m venv env

# Set up and activate the virtual environment
RUN source env/bin/activate

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that your Flask app listens on
EXPOSE 2800

# Set the environment variables
ENV FLASK_APP=app.py

# Start the Flask app
CMD ["python", "app.py"]
