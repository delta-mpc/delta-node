import grpc

from . import mpc_pb2_grpc
from ... import config

channel = grpc.insecure_channel(config.chain_address)
stub = mpc_pb2_grpc.MpcStub(channel)
