#!/bin/bash
docker build . -f docker/Dockerfile  -t subway-test
docker run -h test subway-test
#docker run -v ${SUBWAY_DIR}:/work/subway -h test subway-test