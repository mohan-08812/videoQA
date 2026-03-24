# Use Python 3.10 slim image suitable for ML
FROM python:3.10-slim

# Install system dependencies required for OpenCV and ffmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set up a non-root user for Hugging Face Spaces compatibility
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Upgrade pip and install an older setuptools (v70+ removed pkg_resources which breaks openai-whisper)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir "setuptools<70.0.0" wheel

# Set early environment variables
ENV HOST=0.0.0.0
ENV PORT=7860

# Set working directory
WORKDIR /home/user/app

# Copy the backend requirements first for better caching
COPY --chown=user backend/requirements.txt ./backend/

# IMPORTANT: Install CPU-only PyTorch. 
# The default PyTorch library is a massive 2.5GB and often crashes the free Hugging Face builder. The CPU version is ~200MB!
RUN pip install --no-cache-dir torch==2.2.2 torchvision==0.17.2 --index-url https://download.pytorch.org/whl/cpu

# Install the rest (using --no-build-isolation so it uses our downgraded setuptools instead of fetching the latest broken one)
RUN pip install --no-cache-dir --no-build-isolation -r backend/requirements.txt

# Create necessary directories
RUN mkdir -p /home/user/app/backend/uploads /home/user/app/backend/outputs /home/user/app/backend/frames

# Copy the rest of the application
COPY --chown=user . .

# Expose port (7860 is default for Hugging Face Spaces Docker)
EXPOSE 7860

# Change to the backend directory and run Uvicorn
WORKDIR /home/user/app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
