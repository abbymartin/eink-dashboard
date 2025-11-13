#!/bin/sh
# Name: Dashboard
# Author: abbyv

FBINK_PATH="/mnt/us/libkh/bin/fbink"
SERVER_PATH="192.168.99.147:5000/dash"
OUTPUT_PATH="/mnt/us/tmp/dash1.png"

curl -o $OUTPUT_PATH $SERVER_PATH
$FBINK_PATH -G -c -g file=$OUTPUT_PATH
sleep 2m