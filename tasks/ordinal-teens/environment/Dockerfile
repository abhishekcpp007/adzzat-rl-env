FROM python:3.12-slim@sha256:4840d514c583a4d3d8cad3940e68dee6f0f6f3635c12fcd0a3d74c21a5b93a54
RUN pip install --no-cache-dir pytest==8.3.3 \
 && useradd --create-home --uid 1000 agent
WORKDIR /app
COPY app/ /app/
RUN chown -R agent:agent /app
