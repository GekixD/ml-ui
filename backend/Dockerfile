# Use Python 3.10 (or match your system’s Python version)
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the Flask port
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
