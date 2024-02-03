# Use the official NVIDIA CUDA image as the base image
FROM nvidia/cuda:12.2.2-base-ubuntu20.04

WORKDIR /app

COPY requirements.txt .

# Install system dependencies
RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y python3 python3-pip ffmpeg libsm6 libxext6 git

# Install Python dependencies
RUN pip3 install --upgrade pip && pip3 install  --no-cache-dir -r requirements.txt

# Expose the FastAPI port
EXPOSE 8000

COPY . .

# Command to run the application

#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

