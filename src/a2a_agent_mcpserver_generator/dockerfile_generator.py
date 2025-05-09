def generate_docker_files(notification_receiver_port: str):
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

# 从 builder 复制虚拟环境
COPY --from=builder /app/.venv ./.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE {notification_receiver_port}

CMD ["python", "server.py"]
'''
    return dockerfile