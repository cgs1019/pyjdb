#!/bin/bash

dir=$(cd $(dirname $0) && pwd)

tcpdump \
  -i lo0 \
  -X \
  "tcp port 5995 and (((ip[2:2] - ((ip[0] & 0xf) << 2)) - ((tcp[12] & 0xf0) >> 2)) != 0)"
