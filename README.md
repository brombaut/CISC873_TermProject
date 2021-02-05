# CISC873_TermProject

## NOTE: All scripts should be run from the root of this project

All data collection and transformation scripts are located in _data_transform_scripts_.

All analysis was done in _analytics_

## Repository List

Inside _repo_collection_ are relevant files for determining the list of client projects we examin.

- `repos_from_DLScents.csv` is a list of deep learning projects that was used in The Scent of Deep Learning Code (https://dl.acm.org/doi/10.1145/3379597.3387479).
- `aoo_repo_scraper.py` is a script that can retrieve repository names from the Awesome Open Source website (https://awesomeopensource.com/). You'll notice at the start of the script is AOO_CATEGORIES list. You uncomment the categories you want to retrieve projects for (might take a while if you uncomment all of them at once). The collected project repo names are stored in `aoo_repos.json`.
- `aoo_repos.json` holds the repo name for each project we've collected data on.

## Extracting Imports and Call Statements

#### _extract_imports_and_calls.sh_

The `extract_imports_and_calls.sh` script is the driver for this process. You just have to make sure you put a list of projects you want to collect data for into the `repos` array at the start of the script, and it will collect all the import and call statements for that project using the following process:

- For every project, clone the repo from github
- Fetch all tags for the project (these tags are used as releases)
- Checkout each tag in the order the tags were created (e.g. Checkout tag v1.0, then tag v1.1, then tagv1.2, etc.).
- Call python script `./repo_analyzer.py` with the relevant arguments (i.e. repo name, current version of the repo we have checked out)(explained below).
- Call python script `./data_transform_scripts/write_repo_release_to_csv.py` with relevant arguments to save the record of the repo and release we just analyzed to a csv.

- At the end of the script, `data_transform_scripts/parse_import_jsons_to_csv.py` and `data_transform_scripts/parse_call_jsons_to_csv.py` py scripts are called, which parse all the jsons previously created and adds them all to a single csv file.
- Also, all the json files will be deleted, since all that info has been parsed into the csvs.

#### _repo_analyzer.py_

This script is called with arguments that specify the path to the local cloned repository it is going to analyzed, the name of the repository, and the currently checkout out tag (version) of the repository. The script finds all the python files in the project that import one of the Deep Learning libraries using the _LibraryImportsFinder_ (found in `data_transform_scripts.library_imports_finder`), and extracts the imports of each file using the _ImportsParser_ (found in `data_transform_scripts.source_imports_parser`), and the calls of each file using the _FunctionCallsCollector_ (found in data_transform_scripts.function_calls_collector). All this data is saved as JSON files, which will later be parsed into CSV files.

## Parsing the Import and Call diffs across releases (time)

#### _extract_diffs_and_timelines.sh_
