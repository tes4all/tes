FROM python:3.14-slim-trixie AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/

RUN apt-get update && apt-get -y upgrade && apt-get install -y python3-dev gcc build-essential

WORKDIR /packages
COPY requirements.txt .
RUN uv venv .venv && \
    uv pip install --no-cache -r requirements.txt

FROM python:3.14-slim-trixie

COPY --from=builder /packages/.venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home appuser && \
    mkdir -p /certs/config && \
    mkdir -p /certs/certificates

WORKDIR /home/appuser
COPY main.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Entrypoint runs as root to fix perms, then drops to appuser
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "-u", "main.py"]
