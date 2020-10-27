import argparse
import subprocess
import os

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dir', help="search directory or file", default='.',)
parser.add_argument('-l', '--library', help="ML library to search for", default='tensorflow',)


def run():
    args = parser.parse_args()
    if os.path.isfile(args.dir):
        print("ERROR: -d --dir arg should be directory.")
        exit(1)
    file_that_import_library = search_project(args.dir, args.library)


def search_project(project_directory, library):
    print(project_directory)
    print(library)
    astpath_command = "astpath -d '{}' '//Import/names//alias[@name=\"{}\"]'".format(project_directory, library)
    process = subprocess.Popen(astpath_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print(output)
    print(error)


if __name__ == "__main__":
    run()
