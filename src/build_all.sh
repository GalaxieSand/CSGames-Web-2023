#! /bin/bash

cd IdServer
./build_docker.sh

cd ../RepositoryService
./build_docker.sh

cd ../SnippetsService
./build_docker.sh

cd ../webdocs
docker build -t webdocs:latest .

cd ../GitRepoAnonymizer
docker build -t repoanonymizer:latest .

