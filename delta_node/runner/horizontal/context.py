from __future__ import annotations

import logging
import os
import shutil
from typing import Any, List, Tuple

from delta.core.task import (
    AggResultType,
    ClientContext,
    DataFormat,
    DataLocation,
    DataNode,
    InputGraphNode,
)
from delta_node import dataset, pool, serialize
from delta_node.runner import loc

from .commu import CommuClient

_logger = logging.getLogger(__name__)


class ClientTaskContext(ClientContext):
    def __init__(self, task_id: str, cache_size_limit: int = 100000000) -> None:
        self.task_id = task_id
        self.cache_size_limit = cache_size_limit
        self.cache: pool.MPCache[str, Any] = pool.MPCache()
        self.agg_result: pool.MPCache[str, AggResultType] = pool.MPCache()

    def get(self, *vars: DataNode) -> List[Any]:
        def get_var(var: DataNode) -> Any:
            value = None
            filename = loc.task_context_file(self.task_id, var.name)

            if var.name in self.cache:
                value = self.cache[var.name]
            elif os.path.exists(filename):
                value = serialize.load_obj(filename)
                file_size = os.path.getsize(filename)
                if var.name not in self.cache and self.cache.size + file_size < self.cache_size_limit:
                    self.cache[var.name] = value
            elif var.location == DataLocation.CLIENT:
                if isinstance(var, InputGraphNode):
                    if var.filename is not None and var.format is not None:
                        value = self.load_data(var.filename, var.format, **var.kwargs)
                    elif var.default is not None:
                        value = var.default
            else:
                raise ValueError(
                    f"Cannot get server var {var.name} in client. You should download and set it first."
                )
            if value is None:
                raise ValueError(f"Cannot get var {var.name}")
            return value

        if len(vars) == 0:
            return []
        elif len(vars) == 1:
            return [get_var(vars[0])]
        else:
            return list(pool.map_in_io(get_var, vars))

    def download(self, client: CommuClient, var: DataNode):
        assert var.location == DataLocation.SERVER

        filename = loc.task_context_file(self.task_id, var.name)

        with open(filename, mode="wb") as f:
            client.download_task_context(self.task_id, var.name, f)

        value = serialize.load_obj(filename)
        self.cache[var.name] = value

    def set(self, *pairs: Tuple[DataNode, Any]):
        def set_var(var: DataNode, data: Any):
            filename = loc.task_context_file(self.task_id, var.name)
            serialize.dump_obj(filename, data)
            file_size = os.path.getsize(filename)
            if self.cache.size + file_size < self.cache_size_limit:
                self.cache[var.name] = data

        if len(pairs) == 1:
            set_var(*pairs[0])
        else:
            vars, datas = zip(*pairs)
            return list(pool.map_in_io(set_var, vars, datas))

    def has(self, var: DataNode) -> bool:
        if var.location == DataLocation.SERVER:
            return False
        filename = loc.task_context_file(self.task_id, var.name)
        if os.path.exists(filename):
            return True
        if isinstance(var, InputGraphNode):
            if var.filename is not None and var.format is not None:
                return dataset.check_dataset(var.filename)
            if var.default is not None:
                return True
        return False

    def upload(self, name: str, result: AggResultType):
        _logger.debug(f"upload agg var name {name}")
        self.agg_result[name] = result

    def get_agg_result(self, name: str) -> AggResultType:
        _logger.debug(f"get agg var name {name}")
        return self.agg_result.pop(name)

    def load_data(self, filename: str, format: DataFormat, **kwargs: Any):
        if format == DataFormat.DATASET:
            return dataset.load_dataset(filename, **kwargs)
        elif format == DataFormat.DATAFRAME:
            return dataset.load_dataframe(filename)
        else:
            raise ValueError(f"unknown data format {format}")

    def clear(self):
        self.cache.clear()
        self.agg_result.clear()

        dirname = loc.task_context_dir(self.task_id)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
