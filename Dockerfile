FROM python:3.8-buster as builder

WORKDIR /app

COPY delta_node /app/delta_node
COPY setup.py /app/setup.py

RUN pip wheel -w whls torch==1.8.2+cpu torchvision==0.9.2+cpu torchaudio===0.8.2 -f https://download.pytorch.org/whl/lts/1.8/torch_lts.html
RUN pip wheel -w whls .

FROM python:3.8-slim-buster

WORKDIR /app

COPY --from=builder /app/whls /app/whls

RUN pip install --no-cache-dir whls/*.whl &&  rm -rf whls
ENTRYPOINT [ "delte_node_start" ]
CMD [ "run" ]