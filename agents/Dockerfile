# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11-slim
FROM python:${PYTHON_VERSION}

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps logs unbuffered
ENV PYTHONUNBUFFERED=1



# Install minimal build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Install Python requirements from root build context
COPY agents/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# ===== Runtime config =====
# Expose LiveKit agent port
EXPOSE 7880

CMD ["python3","agents/agent.py", "dev"]



