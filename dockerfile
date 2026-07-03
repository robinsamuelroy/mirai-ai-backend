# Dockerfile

# base image — slim variant is smaller, no unnecessary packages
FROM python:3.13-slim
# set working directory inside container
WORKDIR /app

ENV PYTHONPATH=/app/src

# environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1
# don't write .pyc files — saves disk space in container

ENV PYTHONUNBUFFERED=1
# don't buffer stdout/stderr — logs appear immediately
# critical for seeing FastAPI logs in Docker

# install system dependencies first
# separate from pip install so Docker can cache this layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    # gcc        → needed to compile some Python packages
    # libpq-dev  → needed for psycopg2 (PostgreSQL driver)
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# copy requirements first
# Docker caches layers — if requirements.txt hasn't changed,
# it won't reinstall packages on every build
COPY requirements.txt .

# install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy source code
COPY src/ ./src/

# create directories that the app needs at runtime
RUN mkdir -p uploads chroma_db

# expose port
EXPOSE 8000

# command to run the application
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# host 0.0.0.0 → listen on all interfaces inside container
# without this, container is unreachable from outside