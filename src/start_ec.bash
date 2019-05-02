#!/usr/bin/env bash

cd .
nohup python3 main.py server &
sleep 2
python3 main.py client -q synch