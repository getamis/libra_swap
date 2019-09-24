#!/bin/sh

python -m grpc_tools.protoc \
	-I libraswap/proto \
	--python_out=libraswap/lib \
	--grpc_python_out=libraswap/lib \
	libraswap/proto/*.proto