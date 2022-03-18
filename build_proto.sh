#!/bin/sh

set -e

. ./.venv/bin/activate

exec python3 -m grpc_tools.protoc -Idelta_node/chain --python_out=delta_node/chain --grpclib_python_out=delta_node/chain --mypy_out=delta_node/chain delta_node/chain/chain.proto