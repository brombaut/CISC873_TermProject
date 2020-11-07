# CISC873_TermProject

## Pipeline Stages

### Repo Analyzer

If testing, run one of the following options. The example repo should be cloned into the `examples/<REPO>` folder

```bash
# Default to tangent
python data_transform_scripts/repo_analyzer.py -t
# Can also specify the test project
python data_transform_scripts/repo_analyzer.py -t neuralint
```

### Parse To CSVs

Parse import jsons generated from the repo analyzer section and add the rows to the `data/csv/imports.csv` file

```bash
python data_transform_scripts/parse_import_jsons_to_csv.py
```
