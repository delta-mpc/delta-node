import argparse
import asyncio
import os
from typing import Optional, Sequence


async def _run():
    from delta_node import (app, chain, commu, config, coord, db, log, pool,
                            registry, runner)

    if len(config.chain_host) == 0:
        raise RuntimeError("chain connector host is required")
    if len(config.node_url) == 0:
        raise RuntimeError("node host is required")
    if len(config.node_name) == 0:
        raise RuntimeError("node name is required")

    listener = log.create_log_listener()
    listener.start()
    log.init()

    loop = asyncio.get_event_loop()
    loop.set_default_executor(pool.IO_POOL)
    await db.init(config.db)
    chain.init(config.chain_host, config.chain_port, ssl=False)
    await registry.register(config.node_url, config.node_name)
    await commu.init()

    fut = asyncio.gather(
        app.run("0.0.0.0", config.api_port), runner.run(), coord.run_unfinished_tasks()
    )
    try:
        await fut
    finally:
        await commu.close()
        await registry.unregister()
        chain.close()
        await db.close()
        listener.stop()


def run():
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass


def init():
    config_file = os.getenv("DELTA_NODE_CONFIG", "config/config.yaml")
    config_dir, _ = os.path.split(config_file)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)

    if not os.path.exists(config_file):
        from .config_example import config_example_str

        with open(config_file, mode="w", encoding="utf-8") as f:
            f.write(config_example_str)

    from . import config

    if not os.path.exists(config.task_dir):
        os.makedirs(config.task_dir, exist_ok=True)

    if not os.path.exists(config.data_dir):
        os.makedirs(config.data_dir, exist_ok=True)

    if not os.path.exists(config.log_dir):
        os.makedirs(config.log_dir, exist_ok=True)


def mnist():
    from . import mnist

    mnist.mnist_train()


def main(input_args: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description="delta node", prog="Delta Node")
    parser.add_argument(
        "action",
        choices=["init", "run", "get-mnist"],
        help="delta node start action: 'init' to init delta node config, 'run' to start the node",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")
    args = parser.parse_args(input_args)
    if args.action == "init":
        init()
    elif args.action == "run":
        run()
    elif args.action == "get-mnist":
        mnist()
