#!/bin/bash

# TODO: List of repos
declare -a repos=(
  "google/tangent"
  "tensorflow/ranking"
)

source env/bin/activate
REPOS_DATA_DIR=./data/repos/
for repo in "${repos[@]}"
do
  repo_dir=$(tr '/' '#' <<< "$repo")
  # If the project directory doesn't exist, make the directory and clone the project
  if [ ! -d "${REPOS_DATA_DIR}${repo_dir}" ] 
  then
    mkdir ./data/repos/${repo_dir}
    git clone git@github.com:${repo}.git ${REPOS_DATA_DIR}${repo_dir}
  fi
  cd ${REPOS_DATA_DIR}${repo_dir}
  git fetch --all --tags
  tags=$(git tag --list)
  while read -r tag
  do
      echo "TAG $tag"
      git checkout $tag
      cd ../../../
      python ./repo-analyzer/main.py --dir ${REPOS_DATA_DIR}${repo_dir} --repo $repo --repoversion $tag
      cd ${REPOS_DATA_DIR}${repo_dir}
  done <<< "$tags"
  cd ../../../
  rm -rf ${REPOS_DATA_DIR}${repo_dir}
done


# Extract all into single csv
python repo-analyzer/parse_import_jsons_to_csv.py