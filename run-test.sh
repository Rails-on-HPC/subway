#!/bin/bash
docker build . -f docker/Dockerfile  -t subway-test &&
docker run -h test --name subway-container subway-test &&
#docker run -v ${SUBWAY_DIR}:/work/subway -h test subway-test &&
docker cp subway-container:/work/subway/coverage.xml ./coverage.xml