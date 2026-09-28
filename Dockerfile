FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files to disc and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv for fast dependency resolution
RUN pip install uv

# Copy only the files needed for installation to leverage Docker cache
COPY pyproject.toml uv.lock README.md ./

# Install dependencies without installing the project itself
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Install the project
RUN uv sync --frozen --no-dev

# Create a non-root user
RUN useradd -m appuser && chown -R appuser /app
# Prepare data directory for SQLite
RUN mkdir -p /data && chown -R appuser /data

USER appuser

# Expose port
EXPOSE 8000

# Healthcheck without curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD /app/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run Uvicorn
CMD ["/app/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
