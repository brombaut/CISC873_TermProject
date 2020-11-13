import csv
import json
import os

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
IMPORTS_FILE = "./data/csv/imports.csv"
IMPORT_FIELD_NAMES = [
    "file",
    "file_in_repo",
    "repo",
    "repo_version",
    "name",
    "asname",
    "module"
]

IMPORT_DIFFS_FILE = "./data/csv/import_diffs.csv"
IMPORT_DIFFS_FIELD_NAMES = [
    "repo",
    "file",
    "old_release",
    "new_release",
    "type",
    "import_name",
    "import_asname",
    "import_module"
]

REPO_IMPORTS_FILE = "./data/csv/repo_imports.csv"
REPO_IMPORTS_FIELD_NAMES = [
    "repo",
    "version",
    "import_name",
    "import_asname",
    "import_module"
]


class Change:
    def __init__(self, type, import_obj):
        self.type = type
        self.import_obj = import_obj


class Diff:
    def __init__(self, repo, file, old_release, new_release):
        self.repo = repo
        self.old_release = old_release
        self.new_release = new_release
        self.file = file
        self.changes = list()

    def import_added(self, import_obj):
        self.changes.append(Change("ADD", import_obj))

    def import_deleted(self, import_obj):
        self.changes.append(Change("DELETE", import_obj))


class Import:
    def __init__(self, name, asname, module):
        self.name = name
        self.asname = asname
        self.module = module


class RepoFile:
    def __init__(self, file):
        self.file_name = file
        self.imports = dict()

    def add_import(self, import_line):
        import_name = import_line['name']
        if import_name not in self.imports:
            self.imports[import_name] = Import(import_name, import_line['asname'], import_line['module'])

    def has_import(self, import_name):
        return import_name in self.imports


class Release:
    def __init__(self, release, release_number):
        self.release = release
        self.release_number = release_number
        self.files = dict()

    def add_import(self, import_line):
        file = import_line['file_in_repo']
        if file not in self.files:
            self.files[file] = RepoFile(file)
        self.files[file].add_import(import_line)

    def get_diffs(self, repo, previous_release_obj):
        file_diffs = dict()
        # Loop over new release files, if any not in old release file, track
        for new_file in self.files.values():
            file_name = new_file.file_name
            if file_name not in file_diffs:
                prev_release = previous_release_obj.release if previous_release_obj is not None else None
                file_diffs[file_name] = Diff(repo, file_name, prev_release, self.release)
            old_file = previous_release_obj.files[file_name] if previous_release_obj is not None and file_name in previous_release_obj.files else None
            for new_import in new_file.imports.values():  # Loop over all imports in new_file
                if old_file is None or not old_file.has_import(new_import.name):  # If file didnt exist in prev version or file didn't have the import in the previous version
                    file_diffs[file_name].import_added(new_import)
        # Loop over old release files, if any not in new release file, track
        if previous_release_obj is not None:
            for old_file in previous_release_obj.files.values():
                if old_file.file_name not in file_diffs:
                    file_diffs[old_file.file_name] = Diff(repo, old_file.file_name, previous_release_obj.release, self.release)
                new_file = self.files[old_file.file_name] if old_file.file_name in self.files else None
                for old_import in old_file.imports.values():  # Loop over all imports from prev version of file
                    # If file was deleted from prev version to new version, or if the old version has an import that the new version doesn't
                    if new_file is None or not new_file.has_import(old_import.name):
                        file_diffs[old_file.file_name].import_deleted(old_import)
        return list(file_diffs.values())

    def get_release_imports(self, repo):
        release_imports = dict()
        for repo_file in self.files.values():
            for key, import_obj in repo_file.imports.items():
                result = {
                    "repo": repo,
                    "version": self.release,
                    "import_name": import_obj.name,
                    "import_asname": import_obj.asname,
                    "import_module": import_obj.module
                }
                release_imports[key] = result
        return list(release_imports.values())


class Repo:
    def __init__(self, repo):
        self.repo = repo
        self.releases = dict()
        self.diffs = list()
        self.repo_imports = list()

    def add_release(self, release):
        self.releases[release.release] = release

    def add_import(self, import_line):
        release = import_line['repo_version']
        self.releases[release].add_import(import_line)

    def parse_diffs(self):
        sorted_releases = self._get_sorted_releases()
        old_release = None
        for rel in sorted_releases.values():
            new_release = rel
            diffs_across_release = new_release.get_diffs(self.repo, old_release)
            self.diffs.extend(diffs_across_release)
            old_release = new_release

    def parse_repo_imports(self):
        sorted_releases = self._get_sorted_releases()
        for rel in sorted_releases.values():
            imports_for_release = rel.get_release_imports(self.repo)
            self.repo_imports.extend(imports_for_release)

    def _get_sorted_releases(self):
        result = {k: v for k, v in sorted(self.releases.items(), key=lambda item: int(item[1].release_number))}
        return result


def main():
    releases_list = read_csv(RELEASES_FILE, RELEASE_FIELD_NAMES)
    repos = build_repos_from_releases(releases_list)
    imports_list = read_csv(IMPORTS_FILE, IMPORT_FIELD_NAMES)
    add_imports_data_to_repos(imports_list, repos)
    for repo in repos.values():
        repo.parse_diffs()
        repo.parse_repo_imports()
    diffs = list()
    repo_imports = list()
    for repo in repos.values():
        diffs.extend(repo.diffs)
        repo_imports.extend(repo.repo_imports)

    diffs_for_csv = transform_diffs_to_csv_writable_objects(diffs)
    create_csv_file_if_necessary(IMPORT_DIFFS_FILE, IMPORT_DIFFS_FIELD_NAMES)
    write_lines(IMPORT_DIFFS_FILE, IMPORT_DIFFS_FIELD_NAMES, diffs_for_csv)

    create_csv_file_if_necessary(REPO_IMPORTS_FILE, REPO_IMPORTS_FIELD_NAMES)
    write_lines(REPO_IMPORTS_FILE, REPO_IMPORTS_FIELD_NAMES, repo_imports)


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


def add_imports_data_to_repos(imports_list, repos):
    for import_line in imports_list:
        repo = import_line['repo']
        # if repo not in repos:
        #     repos[repo] = Repo(repo)
        repos[repo].add_import(import_line)


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
                "import_name": change.import_obj.name,
                "import_asname": change.import_obj.asname,
                "import_module": change.import_obj.module
            }
            result.append(all_change_info)
    return result


def create_csv_file_if_necessary(file_path, headers):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, headers)
            writer.writeheader()


def write_lines(output_file_path, headers, dicts_to_write):
    with open(output_file_path, 'a') as csv_file:
        writer = csv.DictWriter(csv_file, headers)
        for line in dicts_to_write:
            writer.writerow(line)


if __name__ == "__main__":
    main()
