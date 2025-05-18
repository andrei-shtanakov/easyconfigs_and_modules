#!/usr/bin/env python3
"""
Compare EasyBuild Modules and EB Files

This script compares a list of installed modules with available EasyBuild (EB) files.
It identifies modules that don't have corresponding EB files and EB files that don't
have corresponding modules. The results are written to two output files.

Usage:
    python compare_eb_modules.py <root_path> <modules_file> [options]

Arguments:
    root_path     - Root directory to search for .eb files
    modules_file  - File containing list of installed modules

Options:
    -v, --verbose - Show examples of mismatches in the summary
    --examples N  - Number of examples to show in verbose mode (default: 5)

Output:
    ext_eb_repo.txt  - List of EB files without corresponding modules
    ext_modules.txt  - List of modules without corresponding EB files

Example:
    python compare_eb_modules.py /path/to/easyconfigs /path/to/modules_list.txt -v

Notes:
    - Module names with '/' in the modules file are converted to '-' to match
      EB file naming conventions
    - Directory entries (ending with '/') and path entries (containing ':') are skipped
    - Module entries without version numbers are skipped
"""

import os
import sys
import glob
import argparse


def read_modules_list(file_path):
    """
    Read modules list from file and filter out non-module entries.
    
    Args:
        file_path (str): Path to the file containing the list of modules
        
    Returns:
        list: List of module names after filtering and converting '/' to '-'
        
    Notes:
        - Entries ending with '/' (directory entries) are skipped
        - Entries containing ':' (path entries) are skipped
        - Entries without version numbers (no digits) are skipped
        - '/' characters in module names are converted to '-' to match EB file naming
    """
    modules = []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Process lines and filter out unwanted entries
    for line in lines:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue
        # Skip directory-only entries (ending with /) - these are module categories
        if line.endswith('/'):
            continue
        # Skip path entries (containing :)
        if ':' in line:
            continue
        # Skip entries that are just module names without versions
        # These typically appear as standalone entries before their versioned variants
        if '/' in line and not any(c.isdigit() for c in line):
            continue
        # Keep only actual module entries
        # Convert '/' to '-' in module names to match EB file naming
        module_name = line.replace('/', '-')
        modules.append(module_name)
    
    return modules


def find_eb_files(root_path):
    """
    Find all .eb files recursively in the given root path.
    
    Args:
        root_path (str): Root directory to search for .eb files
        
    Returns:
        list: List of EB filenames without extensions
        
    Notes:
        - Uses recursive glob pattern to find all .eb files
        - Extracts filename without extension
        - Skips files that don't have digits (likely not proper version-specific EB files)
    """
    eb_files = []
    
    # Find all .eb files
    for eb_file in glob.glob(os.path.join(root_path, '**', '*.eb'), recursive=True):
        # Extract just the filename without extension
        filename = os.path.basename(eb_file)
        name_without_ext = os.path.splitext(filename)[0]
        
        # Skip any files that don't look like proper EB files
        # Most valid EB files will have a version number with digits
        if not any(c.isdigit() for c in name_without_ext):
            continue
            
        eb_files.append(name_without_ext)
    
    return eb_files


def display_examples(items, count=5):
    """
    Display a sample of items up to the specified count.
    
    Args:
        items (iterable): Collection of items to display
        count (int): Maximum number of items to display
        
    Returns:
        str: Formatted string with examples and count of remaining items
        
    Notes:
        - Items are sorted before display
        - If more items exist than count, shows the count of remaining items
        - Returns "None" if items is empty
    """
    if not items:
        return "None"
    
    sample = sorted(items)[:count]
    if len(items) > count:
        return "\n  - " + "\n  - ".join(sample) + f"\n  - ... ({len(items) - count} more)"
    else:
        return "\n  - " + "\n  - ".join(sample)


def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Compare EB files with module list')
    parser.add_argument('root_path', help='Root path to search for .eb files')
    parser.add_argument('modules_file', help='File containing list of modules')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show examples in summary')
    parser.add_argument('--examples', type=int, default=5, help='Number of examples to show in verbose mode (default: 5)')
    
    args = parser.parse_args()
    
    print(f"Analyzing EB files in: {args.root_path}")
    print(f"Reading modules from: {args.modules_file}")
    
    # Read modules list
    modules = read_modules_list(args.modules_file)
    
    # Find .eb files
    eb_files = find_eb_files(args.root_path)
    
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
    
    # Summary report
    print("\nSummary:")
    print(f"Found {len(eb_files)} .eb files and {len(modules)} modules")
    print(f"{len(eb_files_without_modules)} .eb files without corresponding modules")
    print(f"{len(modules_without_eb_files)} modules without corresponding .eb files")
    
    # Display examples if verbose
    if args.verbose:
        print("\nExamples of .eb files without modules:")
        print(display_examples(eb_files_without_modules, args.examples))
        
        print("\nExamples of modules without .eb files:")
        print(display_examples(modules_without_eb_files, args.examples))
    
    print(f"\nResults written to:")
    print(f" - ext_eb_repo.txt: .eb files without modules")
    print(f" - ext_modules.txt: modules without .eb files")


if __name__ == "__main__":
    main()