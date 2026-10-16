#!/usr/bin/env bash
# greet.sh - say hello to the name you give
name="$1"
if [ -z "$name" ]; then
    echo "Usage: $0 NAME"
    exit 1
fi
echo "Hello, $name!"
