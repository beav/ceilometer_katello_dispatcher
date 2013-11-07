#!/bin/bash

echo ""
echo "********* Python stylish tests ***************"
echo "RUNNING: make stylish"
make stylish || exit 1

echo ""
echo "********* Python nosetests ***************"
echo "RUNNING: make"
make || exit 1

