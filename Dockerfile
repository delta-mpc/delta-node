FROM python:3.7-slim

WORKDIR /app

COPY whls /app/delta_node_whls
COPY delta_whls /app/delta_whls

RUN pip install --no-cache-dir delta_node_whls/*.whl && pip install --no-cache-dir delta_whls/*.whl && rm -rf delta_node_whls && rm -rf delta_whls

ENTRYPOINT [ "delte_node_start" ]