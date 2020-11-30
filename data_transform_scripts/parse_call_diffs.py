import csv
import os
import utils

RELEASES_FILE = "./data/csv/releases.csv"
RELEASE_FIELD_NAMES = [
    "repo",
    "version",
    "release_number",
    "year",
    "month",
    "day",
    "time"
]
CALLS_FILE = "./data/csv/calls.csv"
CALL_FIELD_NAMES = [
    "file",
    "file_in_repo",
    "repo",
    "repo_version",
    "name",
    "parent_function"
]

CALL_DIFFS_FILE = "./data/csv/call_diffs.csv"
CALL_DIFFS_FIELD_NAMES = [
    "repo",
    "file",
    "old_release",
    "new_release",
    "type",
    "call_name",
    "call_parent_function",
]

REPO_CALLS_FILE = "./data/csv/repo_calls.csv"
REPO_CALLS_FIELD_NAMES = [
    "repo",
    "version",
    "call_name",
    "call_parent_function",
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


class Change:
    def __init__(self, type, entity):
        self.type = type
        self.entity = entity


class Diff:
    def __init__(self, repo, old_release, new_release):
        self.repo = repo
        self.old_release = old_release
        self.new_release = new_release
        self.changes = list()

    def entity_added(self, entity):
        self.changes.append(Change("ADD", entity))

    def entity_deleted(self, entity):
        self.changes.append(Change("DELETE", entity))


class FileDiff(Diff):
    def __init__(self, repo, file, old_release, new_release):
        super().__init__(repo, old_release, new_release)
        self.file = file


class RepoVersionDiff(Diff):
    def __init__(self, repo, old_release, new_release):
        super().__init__(repo, old_release, new_release)


class TrackedEntity:
    def __init__(self, name):
        self.name = name


class Call(TrackedEntity):
    def __init__(self, name, parent_function):
        super().__init__(name)
        self.parent_function = parent_function


class RepoFile:
    def __init__(self, file):
        self.file_name = file
        self.tracked_entities = dict()

    def add_call(self, call_line):
        call_name = call_line['name']
        if call_name not in self.tracked_entities:
            self.tracked_entities[call_name] = Call(call_line['name'], call_line['parent_function'])

    def has_call(self, entity_name):
        return entity_name in self.tracked_entities


class Release:
    def __init__(self, release, release_number):
        self.release = release
        self.release_number = release_number
        self.files = dict()

    def add_call(self, call_line):
        file = call_line['file_in_repo']
        if file not in self.files:
            self.files[file] = RepoFile(file)
        self.files[file].add_call(call_line)

    def get_diffs(self, repo, previous_release_obj):
        file_diffs = dict()
        # Loop over new release files, if any not in old release file, track
        for new_file in self.files.values():
            file_name = new_file.file_name
            if file_name not in file_diffs:
                prev_release = previous_release_obj.release if previous_release_obj is not None else None
                file_diffs[file_name] = FileDiff(repo, file_name, prev_release, self.release)
            old_file = previous_release_obj.files[file_name] if previous_release_obj is not None and file_name in previous_release_obj.files else None
            for new_call in new_file.tracked_entities.values():  # Loop over all calls in new_file
                if old_file is None or not old_file.has_call(new_call.name):  # If file didnt exist in prev version or file didn't have the call in the previous version
                    file_diffs[file_name].entity_added(new_call)
        # Loop over old release files, if any not in new release file, track
        if previous_release_obj is not None:
            for old_file in previous_release_obj.files.values():
                if old_file.file_name not in file_diffs:
                    file_diffs[old_file.file_name] = FileDiff(repo, old_file.file_name, previous_release_obj.release, self.release)
                new_file = self.files[old_file.file_name] if old_file.file_name in self.files else None
                for old_call in old_file.tracked_entities.values():  # Loop over all calls from prev version of file
                    # If file was deleted from prev version to new version, or if the old version has an import that the new version doesn't
                    if new_file is None or not new_file.has_call(old_call.name):
                        file_diffs[old_file.file_name].entity_deleted(old_call)
        return list(file_diffs.values())

    def get_repo_call_diff(self, repo, previous_release_obj):
        prev_release = previous_release_obj.release if previous_release_obj is not None else None
        diff = RepoVersionDiff(repo, prev_release, self.release)
        # Looking at first release
        if previous_release_obj is None:
            for curr_call in self.get_calls():
                diff.entity_added(curr_call)
            return diff
        for curr_call in self.get_calls():
            # New import not in previous release
            if not previous_release_obj.has_call(curr_call):
                diff.entity_added(curr_call)
        for prev_call in previous_release_obj.get_calls():
            # Import was deleted from prev release to new release
            if not self.has_call(prev_call):
                diff.entity_deleted(prev_call)
        return diff

    def get_calls(self):
        result = dict()
        for repo_file in self.files.values():
            for key, call_obj in repo_file.tracked_entities.items():
                result[call_obj.name] = call_obj
        return list(result.values())

    def has_call(self, call_obj):
        for f in self.files.values():
            if f.has_call(call_obj.name):
                return True
        return False


class Repo:
    def __init__(self, repo):
        self.repo = repo
        self.releases = dict()
        self.diffs = list()
        self.repo_calls = list()
        self.repo_call_diffs = list()

    def add_release(self, release):
        self.releases[release.release] = release

    def add_call(self, call_line):
        release = call_line['repo_version']
        self.releases[release].add_call(call_line)

    def parse_file_call_diffs(self):
        sorted_releases = self._get_sorted_releases()
        old_release = None
        for rel in sorted_releases.values():
            new_release = rel
            diffs_across_release = new_release.get_diffs(self.repo, old_release)
            self.diffs.extend(diffs_across_release)
            old_release = new_release

    def parse_repo_calls(self):
        sorted_releases = self._get_sorted_releases()
        for rel in sorted_releases.values():
            calls_for_release = list()
            for c in rel.get_calls():
                calls_for_release.append({
                    "repo": self.repo,
                    "version": rel.release,
                    "call_name": c.name,
                    "call_parent_function": c.parent_function
                })
            self.repo_calls.extend(calls_for_release)

    def parse_repo_call_diffs(self):
        sorted_releases = self._get_sorted_releases()
        old_release = None
        for rel in sorted_releases.values():
            new_release = rel
            repo_call_diff_across_release = new_release.get_repo_call_diff(self.repo, old_release)
            self.repo_call_diffs.append(repo_call_diff_across_release)
            old_release = new_release

    def _get_sorted_releases(self):
        result = {k: v for k, v in sorted(self.releases.items(), key=lambda item: int(item[1].release_number))}
        return result


def main():
    releases_list = read_csv(RELEASES_FILE, RELEASE_FIELD_NAMES)
    repos = build_repos_from_releases(releases_list)
    calls_list = read_csv(CALLS_FILE, CALL_FIELD_NAMES)
    add_calls_data_to_repos(calls_list, repos)
    for repo in repos.values():
        repo.parse_file_call_diffs()
        repo.parse_repo_calls()
        repo.parse_repo_call_diffs()
    diffs = list()
    repo_calls = list()
    repo_call_diffs = list()
    for repo in repos.values():
        diffs.extend(repo.diffs)
        repo_calls.extend(repo.repo_calls)
        repo_call_diffs.extend(repo.repo_call_diffs)
    # Call Diffs at file level
    diffs_for_csv = transform_diffs_to_csv_writable_objects(diffs)
    utils.create_csv_file(CALL_DIFFS_FILE, CALL_DIFFS_FIELD_NAMES)
    utils.write_lines_to_existing_csv(CALL_DIFFS_FILE, CALL_DIFFS_FIELD_NAMES, diffs_for_csv)
    # Imports at repo level
    utils.create_csv_file(REPO_CALLS_FILE, REPO_CALLS_FIELD_NAMES)
    utils.write_lines_to_existing_csv(REPO_CALLS_FILE, REPO_CALLS_FIELD_NAMES, repo_calls)
    # Import Diffs at repo level
    repo_call_diffs_for_csv = transform_repo_call_diffs_to_csv_writable_objects(repo_call_diffs)
    utils.create_csv_file(REPO_CALL_DIFFS_FILE, REPO_CALL_DIFFS_FIELD_NAMES)
    utils.write_lines_to_existing_csv(REPO_CALL_DIFFS_FILE, REPO_CALL_DIFFS_FIELD_NAMES, repo_call_diffs_for_csv)


def read_csv(file_path, headers):
    print("Reading {}...".format(file_path))
    result = list()
    with open(file_path) as csv_file:
        reader = csv.DictReader(csv_file, headers)
        next(reader, None)  # skip the headers
        for row in reader:
            result.append(row)
    return result


def build_repos_from_releases(releases_list):
    result = dict()
    for rl in releases_list:
        if rl['repo'] not in result:
            result[rl['repo']] = Repo(rl['repo'])
        release = Release(rl['version'], rl['release_number'])
        result[rl['repo']].add_release(release)
    return result


def add_calls_data_to_repos(calls_list, repos):
    for call_line in calls_list:
        repo = call_line['repo']
        # if repo not in repos:
        #     repos[repo] = Repo(repo)
        repos[repo].add_call(call_line)


def transform_diffs_to_csv_writable_objects(diffs):
    result = list()
    for diff in diffs:
        repo = diff.repo
        file = diff.file
        old_release = diff.old_release
        new_release = diff.new_release
        for change in diff.changes:
            all_change_info = {
                "repo": repo,
                "file": file,
                "old_release": old_release,
                "new_release": new_release,
                "type": change.type,
                "call_name": change.entity.name,
                "call_parent_function": change.entity.parent_function,
            }
            result.append(all_change_info)
    return result


def transform_repo_call_diffs_to_csv_writable_objects(diffs):
    result = list()
    for diff in diffs:
        repo = diff.repo
        old_release = diff.old_release
        new_release = diff.new_release
        for change in diff.changes:
            all_change_info = {
                "repo": repo,
                "old_release": old_release,
                "new_release": new_release,
                "type": change.type,
                "call_name": change.entity.name,
                "call_parent_function": change.entity.parent_function,
            }
            result.append(all_change_info)
    return result


if __name__ == "__main__":
    main()
