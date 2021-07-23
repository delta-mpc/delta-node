from .. import config

if config.contract_impl == "substrate":
    from .substrate import *
else:
    raise ImportError("unknown contract impl")
