#!/bin/sh

set -e

. ./.venv/bin/activate

mkdir -p delta_node/chain/identity
mkdir -p delta_node/chain/horizontal
mkdir -p delta_node/chain/datahub
mkdir -p delta_node/chain/hlr
mkdir -p delta_node/chain/subscribe
mkdir -p delta_node/chain/transaction
mkdir -p delta_node/zh

python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/identity --grpclib_python_out=delta_node/chain/identity --mypy_out=delta_node/chain/identity delta_node/proto/identity.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/horizontal --grpclib_python_out=delta_node/chain/horizontal --mypy_out=delta_node/chain/horizontal delta_node/proto/horizontal.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/datahub --grpclib_python_out=delta_node/chain/datahub --mypy_out=delta_node/chain/datahub delta_node/proto/datahub.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/hlr --grpclib_python_out=delta_node/chain/hlr --mypy_out=delta_node/chain/hlr delta_node/proto/hlr.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/subscribe --grpclib_python_out=delta_node/chain/subscribe --mypy_out=delta_node/chain/subscribe delta_node/proto/subscribe.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain/transaction --grpclib_python_out=delta_node/chain/transaction --mypy_out=delta_node/chain/transaction delta_node/proto/transaction.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/zk --grpclib_python_out=delta_node/zk --mypy_out=delta_node/zk delta_node/proto/delta-zk.proto
