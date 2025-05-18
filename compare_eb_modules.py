#!/usr/bin/env python3

import os
import sys
import glob


def read_modules_list(file_path):
    """Read modules list from file and filter out non-module entries."""
    modules = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Process lines and filter out unwanted entries
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip directory-only entries (ending with /)
        if line.endswith('/'):
            continue
        # Skip path entries (containing :)
        if ':' in line:
            continue
        # Keep only actual module entries
        modules.append(line)
    
    return modules


def find_eb_files(root_path):
    """Find all .eb files recursively in the given root path."""
    eb_files = []
    
    # Find all .eb files
    for eb_file in glob.glob(os.path.join(root_path, '**', '*.eb'), recursive=True):
        # Extract just the filename without extension
        filename = os.path.basename(eb_file)
        name_without_ext = os.path.splitext(filename)[0]
        eb_files.append(name_without_ext)
    
    return eb_files


def main():
    if len(sys.argv) != 3:
        print("Usage: python compare_eb_modules.py <root_path> <modules_file>")
        sys.exit(1)
    
    root_path = sys.argv[1]
    modules_file = sys.argv[2]
    
    # Read modules list
    modules = read_modules_list(modules_file)
    
    # Find .eb files
    eb_files = find_eb_files(root_path)
    
    # Convert to sets for easier comparison
    modules_set = set(modules)
    eb_files_set = set(eb_files)
    
    # Find eb files without modules
    eb_files_without_modules = eb_files_set - modules_set
    
    # Find modules without eb files
    modules_without_eb_files = modules_set - eb_files_set
    
    # Write results to files
    with open('ext_eb_repo.txt', 'w') as f:
        for item in sorted(eb_files_without_modules):
            f.write(f"{item}\n")
    
    with open('ext_modules.txt', 'w') as f:
        for item in sorted(modules_without_eb_files):
            f.write(f"{item}\n")
    
    print(f"Results written to ext_eb_repo.txt and ext_modules.txt")
    print(f"Found {len(eb_files)} .eb files and {len(modules)} modules")
    print(f"{len(eb_files_without_modules)} .eb files without modules")
    print(f"{len(modules_without_eb_files)} modules without .eb files")


if __name__ == "__main__":
    main()