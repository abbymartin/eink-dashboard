#!/bin/sh
# Name: Test
# Author: abbyv

IMAGE_URL="192.168.1.100:5000/dash"
OUTPUT_PATH="/tmp/dash1.png"

while sleep 1h
do
    curl -v -o "$OUTPUT_PATH" "$IMAGE_URL"
    /mnt/us/libkh/bin/fbink -i file=$OUTPUT_PATH
done

