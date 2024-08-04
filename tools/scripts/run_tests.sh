#!/usr/bin/bash

test_path=$1
[ -z $test_path ] && test_path="$(pwd)/src"

export PYTHONPATH=${PYTHONPATH}:"$(pwd)/src:${test_path}" &&
./env/bin/py.test --cov=src --cov-report html --cov-report term-missing "${test_path}"
