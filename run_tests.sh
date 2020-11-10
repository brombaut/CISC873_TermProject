#!/bin/bash

source env/bin/activate
python -m unittest discover -s./data_transform_scripts/tests -t ./ -v