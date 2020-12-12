#!/bin/bash

source env/bin/activate

python data_transform_scripts/parse_import_diffs.py
python data_transform_scripts/repo_import_diffs_totals.py

python data_transform_scripts/parse_call_diffs.py
python data_transform_scripts/repo_call_diffs_totals.py