import argparse
import os
from find_ml_library_imports import FindMLLibraryImports
from file_imports_parser import FileImportsParser

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', help="search directory")
parser.add_argument('-r', '--repo', help="repo org/name")
parser.add_argument('-v', '--repoversion', help="repo version")
parser.add_argument('-t', '--testing', help="run as testing", nargs="?", const="tangent")


OUTPUT_DIR = "./data/"
ML_LIBRARIES = [
    "tensorflow",
    "torch"
    # "keras"
    # "numpy"
]


TEST_OPTIONS = {
    'tangent': {
        'dir': './examples/tangent/',
        'repo': 'brombaut/tangent',
        'repoversion': '0.0.0'
    },
    'neuralint': {
        'dir': './examples/neuralint/',
        'repo': 'brombaut/neuralint',
        'repoversion': '0.0.0'
    }
}


def main():
    args = parser.parse_args()
    exit_if_invalid_args(args)
    py_files = get_project_python_files(args.dir)
    ml_library_py_files = get_files_that_import_ml_libs(py_files)
    for file in ml_library_py_files:
        repo_dir = os.path.abspath(args.dir)
        file_path_in_repo = file[len(repo_dir) + 1:]
        fip = FileImportsParser(file, args.repo, args.repoversion, OUTPUT_DIR, file_path_in_repo)
        fip.parse()
        fip.write_to_json()
        # ffcp = FileFunctionCallsParser(file, args.repo)
        # ffcp.find_all()
        # ffcp.export_to_json()


def exit_if_invalid_args(args):
    print(args.testing)
    if args.testing:
        setattr(args, 'dir', TEST_OPTIONS[args.testing]['dir'])
        setattr(args, 'repo', TEST_OPTIONS[args.testing]['repo'])
        setattr(args, 'repoversion', TEST_OPTIONS[args.testing]['repoversion'])
    if args.dir is None or os.path.isfile(args.dir):
        raise SystemExit("ERROR: -d --dir arg should be directory.")
    if args.repo is None:
        raise SystemExit("ERROR: -r --repo arg should be repo org/name.")
    if args.repoversion is None:
        raise SystemExit("ERROR: -v --repoversion arg should be repo release version.")


def get_project_python_files(directory):
    directory = os.path.abspath(directory)
    list_of_files = list()
    for (dirpath, dirnames, filenames) in os.walk(directory):
        py_files = list()
        for file in filenames:
            if file.endswith('.py'):
                py_files.append(os.path.join(dirpath, file))
        list_of_files.extend(py_files)
    return list_of_files


def get_files_that_import_ml_libs(py_files):
    result = list()
    for file in py_files:
        import_checker = FindMLLibraryImports(file, ML_LIBRARIES)
        import_checker.parse()
        if import_checker.file_imports_ml_libraries():
            result.append(file)
    return result


if __name__ == "__main__":
    main()