#!/bin/bash
sudo pip install -r requirements-dev.pip --use-mirrors

echo ""
echo "********* Python stylish tests ***************"
echo "RUNNING: make stylish"
make stylish || exit 1

