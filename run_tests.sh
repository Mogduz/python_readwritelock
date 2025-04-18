#! /bin/bash

python3 -m venv venv
source ./bin/activate
pip install -r requirements.txt
python3 -m pytest
deactivate