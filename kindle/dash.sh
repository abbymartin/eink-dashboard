#!/bin/sh
# Name: Dashboard
# Author: abbyv
# DontUseFbink

FBINK_PATH="/mnt/us/libkh/bin/fbink"
SERVER_PATH="192.168.99.147:5000/dash"
OUTPUT_PATH="/mnt/us/tmp/dash1.png"

while sleep 1m; do
    curl -o $OUTPUT_PATH $SERVER_PATH
    if [ $? -eq 0 ]; then
        $FBINK_PATH -G -c -g file=$OUTPUT_PATH
    else
        echo "Could not get image from server"
        break
    fi
done