def generate_docker_files(notification_receiver_port: str):
    expose_line = ''
    if notification_receiver_port:
        expose_line = f'EXPOSE {notification_receiver_port}'

    dockerfile = f'''
FROM python:3.12-slim as builder

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml  ./

RUN uv venv -p python3.12 && \
    . .venv/bin/activate && \
    uv pip install --no-cache

# ---
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app/.venv ./.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

{expose_line}

CMD ["python", "server.py"]
'''
    return dockerfile