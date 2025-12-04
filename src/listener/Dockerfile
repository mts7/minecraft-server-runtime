FROM python:3.11-slim

# Create working directory
WORKDIR /app

COPY requirements.txt /app/requirements.txt

# Install minimal dependencies
RUN apt-get update && apt-get install -y procps
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONUNBUFFERED=1

# Run the script on container start
CMD ["python3", "-m", "src.listener.listener"]
