FROM python:3.7-slim

WORKDIR /app

COPY whls /app/whls

RUN pip install --no-cache-dir -i https://mirrors.ustc.edu.cn/pypi/web/simple delta_task \
    && pip install --no-cache-dir whls/*.whl \
    && rm -rf whls

ENTRYPOINT [ "delte_node_start" ]
CMD [ "run" ]