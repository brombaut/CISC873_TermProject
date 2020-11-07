#!/bin/bash

# TODO: List of repos
declare -a repos=(
  # "google/tangent"
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
  cd ${REPOS_DATA_DIR}${repo_dir} # CD into repo
  git fetch --all --tags
  # tags=$(git tag --list)
  tags=$(git for-each-ref --sort=creatordate --format '%(refname) %(creatordate)' refs/tags)
  release_count=0
  while read -r tag_line
  do
      echo "TAG $tag_line"
      IFS=' '
      read -a tag_out_array <<< "$tag_line"
      tag="${tag_out_array[0]}"
      tag="${tag##*refs/tags/}" # Rmove the "refs/tags/" prefix
      month="${tag_out_array[2]}"
      day="${tag_out_array[3]}"
      time="${tag_out_array[4]}"
      year="${tag_out_array[5]}"
      git checkout $tag
      cd ../../../  # Back to root level
      
      python ./data_transform_scripts/repo_analyzer.py --dir ${REPOS_DATA_DIR}${repo_dir} --repo $repo --repoversion $tag
      
      python ./data_transform_scripts/write_repo_release_to_csv.py -r $repo -v $tag -n $release_count -y $year -m $month -d $day -t $time
      
      release_count=$((release_count+1))
      
      cd ${REPOS_DATA_DIR}${repo_dir}  # CD into repo
  done <<< "$tags"
  cd ../../../
  rm -rf ${REPOS_DATA_DIR}${repo_dir}
done


# Extract all into single csv
python data_transform_scripts/parse_import_jsons_to_csv.py