from __future__ import annotations

import logging
import os
import shutil
from typing import Any, List, MutableMapping, Tuple

from delta.core.task import (AggResultType, DataLocation, DataNode,
                             InputGraphNode, ServerContext)
from delta_node import pool, serialize
from delta_node.coord import loc

_logger = logging.getLogger(__name__)


class ServerTaskContext(ServerContext):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        self.cache: MutableMapping[str, Any] = pool.MPCache()
        self.agg_result: MutableMapping[str, Tuple[AggResultType, int]] = pool.MPCache()

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
            elif isinstance(var, InputGraphNode):
                value = var.default

            if value is None:
                raise ValueError(f"Cannot get var {var.name}")
            if var.name not in self.cache:
                self.cache[var.name] = value
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
            self.cache[var.name] = data
            filename = loc.task_context_file(self.task_id, var.name)
            serialize.dump_obj(filename, data)
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
        return self.agg_result[name]

    def set_agg_result(self, name: str, result: AggResultType, node_count: int):
        self.agg_result[name] = (result, node_count)

    def clear(self):
        self.cache.clear()
        self.agg_result.clear()

        dirname = loc.task_context_dir(self.task_id)
        if os.path.exists(dirname):
            shutil.rmtree(dirname)

    def get_weight(self):
        return self.get(DataNode("params", DataLocation.SERVER))[0]
