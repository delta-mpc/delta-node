from . import app, contract, config, db, node
import logging


def run():
    logging.basicConfig(level=logging.INFO)
    db.init_db()
    node.register_node()
    event_filter = contract.new_event_filter()
    event_filter.start()
    app.run(config.server_host, config.server_port)
