FROM ghcr.io/astral-sh/uv:0.11.26-python3.13-trixie-slim

# Set environment variables for non-root user
ARG USER_UID=1000
ARG USER_GID=1000

# Create a non-root user to run the application
RUN groupadd --gid $USER_GID appuser \
    && useradd --uid $USER_UID --gid $USER_GID --create-home appuser

WORKDIR /app

# Install dependencies
# Copy the pyproject.toml and uv.lock files first to leverage Docker cache
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .
RUN uv sync --frozen --no-dev

# Set ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]