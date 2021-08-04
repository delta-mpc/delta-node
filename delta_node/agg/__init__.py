from . import simple


_agg_methods = {0: simple.aggregate}

_upload_methods = {0: simple.upload}

def get_agg_method(secure_level: int):
    if secure_level not in _agg_methods:
        raise KeyError(f"no such secure level {secure_level}")
    return _agg_methods[secure_level]


def get_upload_method(secure_level: int):
    if secure_level not in _agg_methods:
        raise KeyError(f"no such secure level {secure_level}")
    return _upload_methods[secure_level]
