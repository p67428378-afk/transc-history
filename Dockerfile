# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Set the FLASK_APP environment variable
ENV FLASK_APP=app.py

# Run the Flask application
# Use a production-ready WSGI server like Gunicorn for deployment
# For development, you can use `flask run --host=0.0.0.0`
CMD ["flask", "run", "--host=0.0.0.0"]
