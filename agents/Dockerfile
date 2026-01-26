# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps logs unbuffered
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user for security
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install minimal build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libssl-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

USER appuser

# Ensure model cache directory exists and is owned by appuser
RUN mkdir -p /home/appuser/.cache && chown -R appuser /home/appuser/.cache

WORKDIR /home/appuser

# Copy dependencies first for caching
COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir -r requirements.txt

# ===== Model pre-download step =====
# Download ML models at build time for faster startup
COPY download_models.py .
RUN python download_models.py

# Copy the app code
COPY . .

# ===== Runtime config =====
# Expose LiveKit agent port
EXPOSE 7880

# Default entrypoint and command
ENTRYPOINT ["python", "agent.py"]
CMD ["start"]



