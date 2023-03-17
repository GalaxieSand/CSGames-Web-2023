#!/bin/bash

mkdir pylib
cp -rv ../RestAPI pylib/.

docker build -t idserver .

rm -rf pylib
