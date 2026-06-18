FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE DATA_LICENSE.md DATA_CARD.md ./
COPY src ./src
COPY data/sample_tasks ./data/sample_tasks
RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["ulamgym-nano", "serve", "--task-dir", "data/sample_tasks", "--host", "0.0.0.0", "--port", "8000"]
