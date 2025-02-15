FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the application port
EXPOSE 3000

# Command to run the application using gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:3000", "app:app"]
