import csv
import json
import os
import glob

INPUT_FILE_SEARCH = "./data/calls/calls@*.json"
OUTPUT_FILE_PATH = "./data/csv/calls.csv"
CALL_FIELD_NAMES = [
    "file",
    "file_in_repo",
    "repo",
    "repo_version",
    "name",
    "parent_function"
]


def main():
    create_csv_file_if_necessary(OUTPUT_FILE_PATH, CALL_FIELD_NAMES)
    print("Finding files to parse that match {}".format(INPUT_FILE_SEARCH))
    files_to_parse = get_list_of_unread_jsons(INPUT_FILE_SEARCH)
    print("Found {} files".format(len(files_to_parse)))
    count = 0
    for call_file in files_to_parse:
        count += 1
        print("{}: Parsing + writing {}".format(count, call_file))
        try:
            calls = parse_calls_from_file(call_file)
        except Exception as ve:
            print("[ERROR] Invalid JSON on file {}. Continuing from next file.".format(call_file))
            continue
        for i in calls:
            write_line(OUTPUT_FILE_PATH, CALL_FIELD_NAMES, i)
        mark_file_as_read(call_file)
    print("DONE")


def create_csv_file_if_necessary(file_path, headers):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, headers)
            writer.writeheader()


def get_list_of_unread_jsons(search_dir_path):
    result = glob.glob("{}".format(search_dir_path))
    return result


def parse_calls_from_file(file_path):
    result = list()
    contents = load_file(file_path)
    for c in contents:
        result.append({
            "file": c['file'],
            "file_in_repo": c['file_in_repo'],
            "repo": c['repo'],
            "repo_version": c['repo_version'],
            "name": c['name'],
            "parent_function": c['parent_function']
        })
    return result
    # result = list()
    # contents = load_file(file_path)
    # file_name = contents['file']
    # repo = contents['repo']
    # repo_version = contents['repo_version']
    # for i in contents['imports']:
    #     i['file'] = contents['file']
    #     i['file_in_repo'] = contents['file_in_repo']
    #     i['repo'] = contents['repo']
    #     i['repo_version'] = contents['repo_version']
    #     result.append(i)
    # return result


def load_file(file_path):
    with open(file_path, 'r') as f:
        json_contents = json.load(f)
    return json_contents


def write_line(output_file_path, headers, call_dict):
    with open(output_file_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writerow(call_dict)


def mark_file_as_read(file_path):
    os.rename(file_path, "{}.READ".format(file_path))


if __name__ == "__main__":
    main()
