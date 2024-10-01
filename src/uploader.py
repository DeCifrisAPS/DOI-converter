#!/usr/bin/env python3
import os
import sys
import json
import requests

def upload_doi_data(collana: str, json_data: dict) -> (bool, [str]):
    print(json_data)
    print(collana)
    return False, ["Did nothing"]

def read_json_file(filename: str) -> dict:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main() -> int:
    """
    Upload DOI data
    """
    if len(sys.argv) < 3 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} file_name.json nome_collana", file=sys.stderr)
        return 1
    filename = sys.argv[1]
    collana = sys.argv[2]
    # read json file(?)
    # run for each article the DOI creation
    json_data = read_json_file(filename)
    ok, error_message = upload_doi_data(collana, json_data)
    if not ok:
        print('\n'.join(error_message), file=sys.stderr)

if __name__ == '__main__':
    sys.exit(main())
