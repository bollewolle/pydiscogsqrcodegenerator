FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev extras)
RUN uv sync --locked --no-dev

# Copy application code
COPY src/ src/
COPY templates/ templates/

# Set environment variables
ENV PYTHONPATH=src \
    FLASK_APP=pydiscogsqrcodegenerator \
    FLASK_ENV=production

EXPOSE 5001

# Run with gunicorn for production
RUN uv pip install gunicorn

# NOTE: single worker + no --preload is intentional. The in-process
# APScheduler starts a background thread inside create_app(); --preload
# would run create_app() in the gunicorn master and the scheduler thread
# would not survive fork() into the workers. Multiple workers would also
# each fire every scan job once. For this personal-scale app one worker
# is plenty.
CMD ["uv", "run", "gunicorn", "--bind", "0.0.0.0:5001", "--workers", "1", "pydiscogsqrcodegenerator:create_app()"]
