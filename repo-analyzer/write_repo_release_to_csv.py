import argparse
import os
import csv

# python repo-analyzer/write_repo_release_to_csv.py -r "brombaut/tangent" -v 0.0.0 -n 1 -y 2019 -m Nov -d 6 -t 15:12:14
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--repo', help="repo org/name")
parser.add_argument('-v', '--repoversion', help="repo version (i.e. tag)")
parser.add_argument('-n', '--release_number', help="release_number")
parser.add_argument('-y', '--year', help="year")
parser.add_argument('-m', '--month', help="month")
parser.add_argument('-d', '--day', help="day")
parser.add_argument('-t', '--time', help="time")


OUTPUT_FILE_PATH = "./data/csv/releases.csv"
RELEASE_FIELD_NAMES = [
    "repo",
    "version",
    "release_number",
    "year",
    "month",
    "day",
    "time"
]


def main():
    args = parser.parse_args()
    create_csv_file_if_necessary(OUTPUT_FILE_PATH)
    line_dict = create_release_line_dict(args)
    write_line(OUTPUT_FILE_PATH, line_dict)


def create_csv_file_if_necessary(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, RELEASE_FIELD_NAMES)
            writer.writeheader()


def create_release_line_dict(args):
    result = dict()
    result['repo'] = args.repo
    result['version'] = args.repoversion
    result['release_number'] = args.release_number
    result['year'] = args.year
    result['month'] = args.month
    result['day'] = args.day
    result['time'] = args.time
    return result


def write_line(output_file_path, release_dict):
    with open(output_file_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, RELEASE_FIELD_NAMES)
        writer.writerow(release_dict)


if __name__ == "__main__":
    main()
