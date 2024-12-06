#!/bin/zsh

# Directory containing the files
dir="/Users/vigji/code/cainjb/source_material/pages"

# Navigate to the directory
cd "$dir" || exit 1

# List all files matching the pattern and sort numerically
files=(page_*.pdf)
files=(${(on)files})

# Loop from the last file to the first
for ((i=${#files[@]}-1; i>=0; i--)); do
    file="${files[i]}"
    # Extract the current index
    current_index=${file##*_}
    current_index=${current_index%.pdf}
    
    # Compute the new index
    new_index=$((current_index + 1))
    new_file="page_${new_index}.pdf"
    
    # Perform the rename
    mv "$file" "$new_file"
done