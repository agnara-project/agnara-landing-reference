# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files to disc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv for fast dependency resolution
RUN pip install uv

# Copy only the files needed for installation to leverage Docker cache
COPY pyproject.toml README.md ./
# For this reference app, we copy everything early as there is no uv.lock yet, 
# but in a real app, you'd generate a lock file and install dependencies first.
# RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application code
COPY . .

# Install dependencies into the system python environment
RUN uv pip install --system -e .

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
# Prepare data directory for SQLite
RUN mkdir -p /data && chown -R appuser /data

USER appuser

# Expose port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
