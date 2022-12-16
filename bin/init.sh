#!/bin/sh

echo "Setting up file structure..."
mkdir -p ./var/primary/mount && mkdir -p ./var/primary/data
mkdir -p ./var/secondary/mount && mkdir -p ./var/secondary/data
mkdir -p ./var/tertiary/mount && mkdir -p ./var/tertiary/data

echo "Adding data to redis"
redis-cli zadd players 3 user:Bob
redis-cli zadd players 2.5 user:James
redis-cli zadd players 2.75 user:Jerry
redis-cli zadd players 2.1 user:Tom

echo "Starting services..."
foreman start
