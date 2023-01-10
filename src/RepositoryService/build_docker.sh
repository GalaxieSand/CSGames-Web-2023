#!/bin/bash

mkdir pylib
cp -rv ../RestAPI pylib/.
cp -rv ../OpenIdClient pylib/.

docker build -t repositoryservice .

rm -rf pylib
