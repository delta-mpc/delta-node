import grpc

from . import mpc_pb2_grpc
from ... import config

channel = grpc.insecure_channel(config.contract_address)
stub = mpc_pb2_grpc.MpcStub(channel)
