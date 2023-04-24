from __future__ import annotations

import os
import logging
import shutil
from typing import Any, MutableMapping, Tuple, List

from delta.core.task import (
    ServerContext,
    DataNode,
    AggResultType,
    DataLocation,
    InputGraphNode,
)

from delta_node import pool, serialize
from delta_node.coord import loc


_logger = logging.getLogger(__name__)


class ServerTaskContext(ServerContext):
    def __init__(self, task_id: str, cache_size_limit: int = 100000000) -> None:
        self.task_id = task_id
        self.cache_size_limit = cache_size_limit
        self.cache: pool.MPCache[str, Any] = pool.MPCache()
        self.agg_result: pool.MPCache[str, Tuple[AggResultType, int]] = pool.MPCache()

    def get(self, *vars: DataNode) -> List[Any]:
        def get_var(var: DataNode) -> Any:
            if var.location == DataLocation.CLIENT:
                raise ValueError(f"Cannot get client var {var.name} in server")
            value = None
            filename = loc.task_context_file(self.task_id, var.name)
            if var.name in self.cache:
                value = self.cache[var.name]
            elif os.path.exists(filename):
                value = serialize.load_obj(filename)
                file_size = os.path.getsize(value)
                if var.name not in self.cache and self.cache.size + file_size < self.cache_size_limit:
                    self.cache[var.name] = value
            elif isinstance(var, InputGraphNode):
                value = var.default

            if value is None:
                raise ValueError(f"Cannot get var {var.name}")
            _logger.debug(f"Get var {var.name} : {value}")
            return value

        if len(vars) == 0:
            return []
        elif len(vars) == 1:
            return [get_var(vars[0])]
        else:
            return list(pool.map_in_io(get_var, vars))

    def set(self, *pairs: Tuple[DataNode, Any]):
        def set_var(var: DataNode, data: Any):
            filename = loc.task_context_file(self.task_id, var.name)
            serialize.dump_obj(filename, data)
            file_size = os.path.getsize(filename)
            if self.cache.size + file_size < self.cache_size_limit:
                self.cache[var.name] = data
            _logger.debug(f"Set var {var.name} : {data}")

        if len(pairs) == 1:
            set_var(*pairs[0])
        elif len(pairs) > 1:
            vars, datas = zip(*pairs)
            return list(pool.map_in_io(set_var, vars, datas))

    def has(self, var: DataNode) -> bool:
        filename = loc.task_context_file(self.task_id, var.name)
        if os.path.exists(filename):
            return True
        if isinstance(var, InputGraphNode) and var.default is not None:
            return True
        return False

    def gather(self, name: str) -> Tuple[AggResultType, int]:
        return self.agg_result.pop(name)

    def set_agg_result(self, name: str, result: AggResultType, node_count: int):
        self.agg_result[name] = (result, node_count)

    def clear(self):
        self.cache.clear()
        self.agg_result.clear()

        dirname = loc.task_context_dir(self.task_id)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
