# =========================
# Stage 1 -> Builder
# =========================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install python packages into custom folder
RUN pip install --prefix=/install -r requirements.txt && \
    pip install --prefix=/install gunicorn


# =========================
# Stage 2 -> Final Image
# =========================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Runtime dependencies only
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "medical_system.wsgi:application", "--bind", "0.0.0.0:8000"]