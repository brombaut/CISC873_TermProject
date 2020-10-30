import csv
import json
import os
import glob

INPUT_FILE_SEARCH = "./data/imports/imports@*.json"
OUTPUT_FILE_PATH = "./data/csv/imports-2020-10-29.csv"
IMPORT_FIELD_NAMES = [
    "file",
    "repo",
    "repo_version",
    "name",
    "asname",
    "module"
]


def main():
    create_csv_file_if_necessary(OUTPUT_FILE_PATH)
    print("Finding files to parse that match {}".format(INPUT_FILE_SEARCH))
    files_to_parse = get_list_of_unread_jsons(INPUT_FILE_SEARCH)
    print("Found {} files".format(len(files_to_parse)))
    count = 0
    for import_file in files_to_parse:
        count += 1
        print("{}: Parsing + writing {}".format(count, import_file))
        try:
            imports = parse_imports_from_file(import_file)
        except Exception as ve:
            print("[ERROR] Invalid JSON on file {}. Continuing from next file.".format(import_file))
            continue
        for i in imports:
            write_line(OUTPUT_FILE_PATH, i)
        mark_file_as_read(import_file)
    print("DONE")


def create_csv_file_if_necessary(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, IMPORT_FIELD_NAMES)
            writer.writeheader()


def get_list_of_unread_jsons(search_dir_path):
    result = glob.glob("{}".format(search_dir_path))
    return result


def parse_imports_from_file(file_path):
    result = list()
    contents = load_file(file_path)
    file_name = contents['file']
    repo = contents['repo']
    repo_version = contents['repo_version']
    for i in contents['imports']:
        i['file'] = contents['file']
        i['repo'] = contents['repo']
        i['repo_version'] = contents['repo_version']
        result.append(i)
    return result


def load_file(file_path):
    with open(file_path, 'r') as f:
        json_contents = json.load(f)
    return json_contents


def parse_pr_event(pr_event):
    result = dict()
    result['pr_event.id'] = pr_event['id']
    result['pr_event.repo_id'] = pr_event['repo']['id']
    result['pr_event.title'] = pr_event['payload']['pull_request']['title']
    result['pr_event.pr_id'] = pr_event['payload']['pull_request']['id']
    return result


def write_line(output_file_path, import_dict):
    with open(output_file_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, IMPORT_FIELD_NAMES)
        writer.writerow(import_dict)


def mark_file_as_read(file_path):
    os.rename(file_path, "{}.READ".format(file_path))


if __name__ == "__main__":
    main()
