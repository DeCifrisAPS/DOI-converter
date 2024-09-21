#!/usr/bin/env python3
import csv
import sys

"""
Overview of the process
1. Read TSV
2. Sanity Check
2a. Error Handling
3. Compile to JSON format

Maybe there will be configuration to sync typescript model with this converter
"""

def read_raw_data(filename: str) -> list[str]:
    """Read Tab-Separated Value file"""
    with open(filename, newline='') as tsvfile:
        return csv.reader(tsvfile, delimiter='\t', quotechar='"')

def write_json_data(filename: str, data: list[str]) -> None:
    """Write JSON file for website"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False) # , indent=4)

def main() -> int:
    """Do stuff"""
    return 0

if __name__ == '__main__':
    sys.exit(main())
