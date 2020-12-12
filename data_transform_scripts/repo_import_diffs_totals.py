import utils


ISO_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

RELEASES_FILE = "./data/csv/releases.csv"
RELEASE_FIELD_NAMES = [
    "repo",
    "version",
    "release_number",
    "year",
    "month",
    "day",
    "date_time",
    "time"
]

REPO_IMPORT_DIFFS_FILE = "./data/csv/repo_import_diffs.csv"
REPO_IMPORT_DIFFS_FIELD_NAMES = [
    "repo",
    "old_release",
    "new_release",
    "type",
    "import_name",
    "import_asname",
    "import_module"
]

REPO_IMPORT_DIFFS_TIMELINE_FILE = "./data/csv/repo_import_diffs_timeline.csv"
REPO_IMPORT_DIFFS_TIMELINE_FIELD_NAMES = [
    "date",
    "import",
    "count",
]


def main():
    releases_lines = utils.read_csv_ignore_headers(RELEASES_FILE, RELEASE_FIELD_NAMES)
    releases = build_releases(releases_lines)
    repo_import_diffs = utils.read_csv_ignore_headers(REPO_IMPORT_DIFFS_FILE, REPO_IMPORT_DIFFS_FIELD_NAMES)
    add_release_dates(repo_import_diffs, releases)
    repo_import_diffs.sort(key=get_release_date)
    timeline = build_timeline(repo_import_diffs)
    flattened_timeline = flatten(timeline)
    utils.create_csv_file(REPO_IMPORT_DIFFS_TIMELINE_FILE, REPO_IMPORT_DIFFS_TIMELINE_FIELD_NAMES)
    utils.write_lines_to_existing_csv(REPO_IMPORT_DIFFS_TIMELINE_FILE, REPO_IMPORT_DIFFS_TIMELINE_FIELD_NAMES, flattened_timeline)


def build_releases(releases_lines):
    result = dict()
    for r in releases_lines:
        repo = r['repo']
        version = r['version']
        release_date = r['date_time']
        if repo not in result:
            result[repo] = dict()
        result[repo][version] = release_date
    return result


def add_release_dates(repo_import_diffs, releases):
    for rid in repo_import_diffs:
        repo = rid['repo']
        release = rid['new_release']
        rid['release_date'] = utils.make_date(releases[repo][release], '%d-%m-%Y')


def get_release_date(import_diff):
    return import_diff.get('release_date')


def build_timeline(repo_import_diffs):
    result = dict()
    tally = dict()
    for rid in repo_import_diffs:
        # import_name = rid['import_module'] if rid['import_module'] is not None else rid['import_name']
        import_name = rid['import_name']
        if import_name not in tally:
            tally[import_name] = 0
        if rid['type'] == "ADD":
            tally[import_name] += 1
        elif rid['type'] == "DELETE":
            tally[import_name] -= 1
        release_date = rid['release_date']
        result[release_date] = dict(tally)
    return result


def flatten(timelines):
    result = list()
    for date, import_counts in timelines.items():
        date_string = utils.make_date_string(date, ISO_DATE_FORMAT)
        for import_name, count in import_counts.items():
            result.append({
                "date": date_string,
                "import": import_name,
                "count": count
            })
    return result


if __name__ == "__main__":
    main()
