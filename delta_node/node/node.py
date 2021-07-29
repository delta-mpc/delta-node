import logging

from sqlalchemy.orm import Session

from .. import config, contract, db, model

_logger = logging.getLogger(__name__)

__all__ = ["register_node", "get_node_id"]

_node_id = None


@db.with_session
def register_node(session: Session = None):
    assert session is not None
    global _node_id
    node = session.query(model.Node).filter(model.Node.url == config.url).one_or_none()
    if node is None:
        _logger.info(
            "unregistered node, start to register node", extra={"app": "server"}
        )
        node_id = contract.register_node(config.url)
        node = model.Node(url=config.url, node_id=node_id)
        session.add(node)
        session.commit()
        _node_id = node_id
        _logger.info(
            f"node register complete, node id: {node_id}", extra={"app": "server"}
        )
    else:
        _node_id = node.node_id
        _logger.info(
            f"registered node, node id: {node.node_id}", extra={"app": "server"}
        )


@db.with_session
def get_node_id(session: Session = None):
    assert session is not None
    global _node_id
    if _node_id is None:
        node = (
            session.query(model.Node).filter(model.Node.url == config.url).one_or_none()
        )
        if node is None:
            _logger.error("node unregistered", extra={"app": "server"})
            raise ValueError("node unregistered")
        _node_id = node.node_id
    return _node_id
