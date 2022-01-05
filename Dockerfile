FROM python:3.8-buster as builder

WORKDIR /app

COPY delta_node /app/delta_node
COPY requirements.txt /app/requirements.txt
COPY setup.py /app/setup.py

RUN pip wheel -w whls -r requirements.txt && pip wheel -w whls --no-deps .

FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=builder /app/whls /app/whls

RUN pip install --no-cache-dir whls/*.whl &&  rm -rf whls
ENTRYPOINT [ "delta_node_start" ]
CMD [ "run" ]