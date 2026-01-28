FROM python:3.14-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/

RUN apt-get update && apt-get -y upgrade && apt-get install -y python3-dev gcc build-essential

WORKDIR /packages

COPY requirements.txt .

ENV PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

RUN uv venv .venv && \
    uv pip install --no-cache -r requirements.txt

FROM python:3.14-slim-trixie

RUN apt-get update && apt-get -y upgrade && apt-get install -y apt-transport-https && rm -rf /var/lib/apt/lists/*

COPY --from=builder /packages/.venv /opt/venv

ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY main.py .

ENTRYPOINT ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
