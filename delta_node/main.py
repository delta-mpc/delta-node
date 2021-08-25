import argparse
import multiprocessing as mp
import os


def app_run(q):
    from . import app, config, log

    log.init(q)
    log.set_log_queue(q)
    app.run("0.0.0.0", config.api_port)


def commu_run(q):
    from . import commu, config, log

    log.init(q)
    log.set_log_queue(q)
    server = commu.CommuServer(f"0.0.0.0:{config.node_port}")
    try:
        server.start()
        server.wait_for_termination()
    finally:
        server.stop()


def executor_run(q):
    from . import executor, log

    log.init(q)
    log.set_log_queue(q)
    executor.run()


def run():
    from . import config, db, log, node

    if config.chain_address is None or len(config.chain_address) == 0:
        raise RuntimeError("chain connector address is required")
    if config.node_host is None or len(config.node_host) == 0:
        raise RuntimeError("node address host is required")

    ctx = mp.get_context("spawn")
    with ctx.Manager() as manager:
        queue = manager.Queue()
        listener = log.create_log_listener(queue)
        log.init(queue)
        db.init_db()
        node.register_node()

        app_process = ctx.Process(target=app_run, args=(queue,))
        app_process.start()

        commu_process = ctx.Process(target=commu_run, args=(queue,))
        commu_process.start()

        contract_process = ctx.Process(target=executor_run, args=(queue,))
        contract_process.start()

        contract_process.join()
        commu_process.join()
        app_process.join()
        listener.stop()


def init():
    config_file = os.getenv("DELTA_NODE_CONFIG", "config/config.yaml")
    config_dir, _ = os.path.split(config_file)
    print(config_dir)
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


def main():
    parser = argparse.ArgumentParser(description="delta node", prog="Delta Node")
    parser.add_argument(
        "action",
        choices=["init", "run", "get-mnist"],
        help="delta node start action: 'init' to init delta node config, 'run' to start the node",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")
    args = parser.parse_args()
    if args.action == "init":
        init()
    elif args.action == "run":
        run()
    elif args.action == "get-mnist":
        mnist()
