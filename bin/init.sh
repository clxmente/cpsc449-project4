#!/bin/sh

echo "Setting up file structure..."
mkdir -p ./var/primary/mount && mkdir -p ./var/primary/data
mkdir -p ./var/secondary/mount && mkdir -p ./var/secondary/data
mkdir -p ./var/tertiary/mount && mkdir -p ./var/tertiary/data

echo "Adding data to redis"
redis-cli DEL players
redis-cli zadd players 3 Tom
redis-cli zadd players 2 Bob
redis-cli zadd players 1 James
redis-cli zadd players 1 Jerry

foreman start --procfile Cluster