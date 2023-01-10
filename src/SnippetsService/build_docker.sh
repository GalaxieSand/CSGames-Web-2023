#!/bin/bash

mkdir pylib
cp -rv ../RestAPI pylib/.
cp -rv ../OpenIdClient pylib/.

docker build -t snippetsservice .

rm -rf pylib
