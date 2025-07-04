#! /bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <directory_path>"
    exit 1
fi

cd "$1" || exit 1

for img in *.jpg; do
  ffmpeg -i "$img" -vf "crop=in_w:in_h-50:0:0" "cropped_$img"
done
