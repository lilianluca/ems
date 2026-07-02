FROM ghcr.io/astral-sh/uv:0.11.26-python3.13-trixie-slim

WORKDIR /app

# Install dependencies
# Copy the pyproject.toml and uv.lock files first to leverage Docker cache
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .
RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]