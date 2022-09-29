import argparse
import asyncio
import os
import signal
from typing import Optional, Sequence


async def _run():
    from delta_node import app, chain, config, db, log, registry, runner, zk

    if len(config.chain_host) == 0:
        raise RuntimeError("chain connector host is required")
    if len(config.node_url) == 0:
        raise RuntimeError("node host is required")
    if len(config.node_name) == 0:
        raise RuntimeError("node name is required")

    loop = asyncio.get_event_loop()

    listener = log.create_log_listener(loop)
    listener.start()
    log.init()

    await db.init(config.db)
    chain.init(config.chain_host, config.chain_port, ssl=False)
    zk.init(config.zk_host, config.zk_port, ssl=False)
    await registry.register(config.node_url, config.node_name)

    runner_fut = asyncio.create_task(runner.run())
    app_fut = asyncio.create_task(app.run("0.0.0.0", config.api_port))

    fut = asyncio.gather(runner_fut, app_fut)
    loop.add_signal_handler(signal.SIGINT, lambda: fut.cancel())
    loop.add_signal_handler(signal.SIGTERM, lambda: fut.cancel())
    try:
        await fut
    finally:
        await registry.unregister()
        chain.close()
        zk.close()
        await db.close()
        listener.stop()


def run():
    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass
    except asyncio.CancelledError:
        pass


async def _leave():
    from delta_node import chain, config, db, log, pool, registry

    if len(config.chain_host) == 0:
        raise RuntimeError("chain connector host is required")
    if len(config.node_url) == 0:
        raise RuntimeError("node host is required")
    if len(config.node_name) == 0:
        raise RuntimeError("node name is required")

    loop = asyncio.get_event_loop()

    listener = log.create_log_listener(loop)
    listener.start()
    log.init()

    await db.init(config.db)
    chain.init(config.chain_host, config.chain_port, ssl=False)
    await registry.unregister()
    chain.close()
    await db.close()
    listener.stop()


def leave():
    asyncio.run(_leave())


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


def main(input_args: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description="delta node", prog="Delta Node")
    parser.add_argument(
        "action",
        choices=[
            "init",
            "run",
            "get-mnist",
            "get-wages",
            "get-iris",
            "get-spector",
            "get-all-data",
            "leave",
        ],
        help="""delta node start action: 
        'init' to init delta node config, 
        'run' to start the node, 
        'get-mnist' to get mnist dataset used for learning example,
        'get-wages' to get wages dataframe used for analytics example,
        'get-iris' to get iris dataframe used for lr example,
        'get-spector' to get spector dataframe used for lr example,
        'get-all-data' to get all memtioned dataset,
        'leave' to unregister from the computing network""",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")
    args = parser.parse_args(input_args)
    if args.action == "init":
        init()
    elif args.action == "run":
        run()
    elif args.action == "get-mnist":
        from .dataset.examples import get_mnist

        get_mnist()
    elif args.action == "get-wages":
        from .dataset.examples import get_wages

        get_wages()
    elif args.action == "get-iris":
        from .dataset.examples import get_iris

        get_iris()
    elif args.action == "get-spector":
        from .dataset.examples import get_spector

        get_spector()
    elif args.action == "get-all-data":
        from .dataset.examples import get_all

        get_all()
    elif args.action == "leave":
        leave()
