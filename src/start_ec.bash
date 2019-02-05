#!/usr/bin/env bash

cd .
nohup python3 main.py &
sleep 1
python3 client/client.py -q synch