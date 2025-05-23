#!/bin/bash

# Ativa o ambiente virtual
source ../.venv/bin/activate

# Unset PYTHONPATH to avoid conflicts with system packages
unset PYTHONPATH

# Set PYTHONPATH to prioritize the virtual environment
export PYTHONPATH="/home/marlonsc/pyauto/.venv/lib/python3.10/site-packages:$PYTHONPATH"

# Executa os testes com mock services
make test 
