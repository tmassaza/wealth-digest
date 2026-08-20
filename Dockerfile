FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN python -m pip install --upgrade pip
RUN python - <<'PY'
from pathlib import Path
import tomllib

data = tomllib.loads(Path('pyproject.toml').read_text())
requirements = '\n'.join(data['project']['dependencies']) + '\n'
Path('/tmp/requirements.txt').write_text(requirements)
PY
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
