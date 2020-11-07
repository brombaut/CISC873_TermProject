#!/bin/bash

tag_line="refs/tags/v0.1.4/4 Tue Nov 7 15:50:11 2017 -0500"
echo "TAG $tag_line"
IFS=' '
read -a tag_out_array <<< "$tag_line"
tag="${tag_out_array[0]}"
tag="${tag##*refs/tags/}"
echo "$tag"

