#!/bin/sh

set -e


mkdir -p delta_node/chain2/identity
mkdir -p delta_node/chain2/horizontal
mkdir -p delta_node/chain2/datahub
mkdir -p delta_node/chain2/hlr
mkdir -p delta_node/chain2/subscribe
mkdir -p delta_node/chain2/transaction
mkdir -p delta_node/zk2

python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/identity --grpc_python_out=delta_node/chain2/identity --pyi_out=delta_node/chain2/identity delta_node/proto/identity.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/horizontal --grpc_python_out=delta_node/chain2/horizontal --pyi_out=delta_node/chain2/horizontal delta_node/proto/horizontal.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/datahub --grpc_python_out=delta_node/chain2/datahub --pyi_out=delta_node/chain2/datahub delta_node/proto/datahub.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/hlr --grpc_python_out=delta_node/chain2/hlr --pyi_out=delta_node/chain2/hlr delta_node/proto/hlr.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/subscribe --grpc_python_out=delta_node/chain2/subscribe --pyi_out=delta_node/chain2/subscribe delta_node/proto/subscribe.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/chain2/transaction --grpc_python_out=delta_node/chain2/transaction --pyi_out=delta_node/chain2/transaction delta_node/proto/transaction.proto
python3 -m grpc_tools.protoc -Idelta_node/proto --python_out=delta_node/zk2 --grpc_python_out=delta_node/zk2 --pyi_out=delta_node/zk2 delta_node/proto/delta-zk.proto
