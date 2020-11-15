import csv
import os
from datetime import datetime, timedelta, timezone


def create_csv_file_if_necessary(file_path, headers):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, headers)
            writer.writeheader()


def create_csv_file(file_path, headers):
    with open(file_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        writer.writeheader()


def read_csv_ignore_headers(file_path, headers):
    result = list()
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file, headers)
        next(reader, None)  # skip the headers
        for row in reader:
            result.append(row)
    return result


def write_lines_to_existing_csv(output_file_path, headers, dicts_to_write):
    with open(output_file_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        for line in dicts_to_write:
            writer.writerow(line)


def write_lines_to_new_csv(output_file_path, headers, dicts_to_write):
    with open(output_file_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        for line in dicts_to_write:
            writer.writerow(line)


def make_date(string, date_format):
    return datetime.strptime(string.replace("Z", "+0000"), date_format)


def make_date_string(date, date_format):
    return date.strftime(date_format)