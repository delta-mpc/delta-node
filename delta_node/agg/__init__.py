from .simple import aggregate as simple_agg


_agg_methods = {1: simple_agg}


def get_agg_method(secure_level: int):
    if secure_level not in _agg_methods:
        raise KeyError(f"no such secure level {secure_level}")
    return _agg_methods[secure_level]
