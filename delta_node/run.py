import logging
import multiprocessing as mp

from . import app, config, db, node, commu, executor


def app_run():
    logging.basicConfig(level=logging.INFO)
    app.run(config.server_host, config.server_port)


def commu_run():
    logging.basicConfig(level=logging.INFO)
    server = commu.CommuServer(config.url)
    try:
        server.start()
        server.wait_for_termination()
    finally:
        server.stop()


def executor_run():
    logging.basicConfig(level=logging.INFO)
    executor.run()


def run():
    logging.basicConfig(level=logging.INFO)
    db.init_db()
    node.register_node()

    ctx = mp.get_context("spawn")

    app_process = ctx.Process(target=app_run)
    app_process.start()

    commu_process = ctx.Process(target=commu_run)
    commu_process.start()

    contract_process = ctx.Process(target=executor_run)
    contract_process.start()

    contract_process.join()
    commu_process.join()
    app_process.join()
