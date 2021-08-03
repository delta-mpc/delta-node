import logging
import multiprocessing as mp

from . import app, config, contract, db, node, commu


def app_run():
    logging.basicConfig(level=logging.INFO)
    app.run(config.server_host, config.server_port)


def commu_run():
    logging.basicConfig(level=logging.INFO)
    server = commu.CommuServer(config.url)
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop()


def contract_run():
    logging.basicConfig(level=logging.INFO)
    event_filter = contract.new_event_filter()
    event_filter.start()
    events = ["Join", "Task", "Train", "PublicKey"]
    try:
        while True:
            for event in events:
                e = event_filter.wait_for_event(event, timeout=1)
                if e:
                    print(e)
    except KeyboardInterrupt:
        event_filter.terminate()
        event_filter.join()


def run():
    db.init_db()
    node.register_node()

    ctx = mp.get_context("spawn")

    app_process = ctx.Process(target=app_run)
    app_process.start()

    commu_process = ctx.Process(target=commu_run)
    commu_process.start()

    contract_process = ctx.Process(target=contract_run)
    contract_process.start()

    contract_process.join()
    commu_process.join()
    app_process.join()
