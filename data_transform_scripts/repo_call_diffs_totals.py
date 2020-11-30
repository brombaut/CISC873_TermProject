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

REPO_CALL_DIFFS_FILE = "./data/csv/repo_call_diffs.csv"
REPO_CALL_DIFFS_FIELD_NAMES = [
    "repo",
    "old_release",
    "new_release",
    "type",
    "call_name",
    "call_parent_function",
]

REPO_CALL_DIFFS_TIMELINE_FILE = "./data/csv/repo_call_diffs_timeline.csv"
REPO_CALL_DIFFS_TIMELINE_FIELD_NAMES = [
    "date",
    "call",
    "count",
]


def main():
    print("Reading releases...")
    releases_lines = utils.read_csv_ignore_headers(RELEASES_FILE, RELEASE_FIELD_NAMES)
    print("Building releases...")
    releases = build_releases(releases_lines)
    print("Reading repo cass diffs...")
    repo_call_diffs = utils.read_csv_ignore_headers(REPO_CALL_DIFFS_FILE, REPO_CALL_DIFFS_FIELD_NAMES)
    print("Adding release dates...")
    add_release_dates(repo_call_diffs, releases)
    print("Sorting repo call diffs")
    repo_call_diffs.sort(key=get_release_date)
    print("Building timeline...")
    timeline = build_timeline(repo_call_diffs)
    print("Flattening timeline...")
    flattened_timeline = flatten(timeline)
    print("Creating output file...")
    utils.create_csv_file(REPO_CALL_DIFFS_TIMELINE_FILE, REPO_CALL_DIFFS_TIMELINE_FIELD_NAMES)
    print("Writing timeline to output file...")
    utils.write_lines_to_existing_csv(REPO_CALL_DIFFS_TIMELINE_FILE, REPO_CALL_DIFFS_TIMELINE_FIELD_NAMES, flattened_timeline)


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


def add_release_dates(repo_call_diffs, releases):
    for rid in repo_call_diffs:
        repo = rid['repo']
        release = rid['new_release']
        rid['release_date'] = utils.make_date(releases[repo][release], '%d-%m-%Y')


def get_release_date(call_diff):
    return call_diff.get('release_date')


def build_timeline(repo_call_diffs):
    result = dict()
    tally = dict()
    count = 0
    total = len(repo_call_diffs)
    for rid in repo_call_diffs:
        count += 1
        print("{}/{}".format(count, total))
        call_name = rid['call_name']
        if call_name not in tally:
            tally[call_name] = 0
        if rid['type'] == "ADD":
            tally[call_name] += 1
        elif rid['type'] == "DELETE":
            tally[call_name] -= 1
        release_date = rid['release_date']
        result[release_date] = dict(tally)
    return result


def flatten(timelines):
    result = list()
    for date, call_counts in timelines.items():
        date_string = utils.make_date_string(date, ISO_DATE_FORMAT)
        for call_name, count in call_counts.items():
            result.append({
                "date": date_string,
                "call": call_name,
                "count": count
            })
    return result


if __name__ == "__main__":
    main()
