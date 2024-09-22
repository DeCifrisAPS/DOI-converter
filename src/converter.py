#!/usr/bin/env python3
import sys

import csv
import json

import re
import codecs

ESCAPE_SEQUENCE_RE = re.compile(r'''
        ( \\U........      # 8-digit hex escapes
        | \\u....          # 4-digit hex escapes
        | \\x..            # 2-digit hex escapes
        | \\[0-7]{1,3}     # Octal escapes
        | \\N\{[^}]+\}     # Unicode characters by name
        | \\[\\'"abfnrtv]  # Single-character escapes
        )''', re.UNICODE | re.VERBOSE)

def decode_escapes(s):
    def decode_match(match):
        try:
            return codecs.decode(match.group(0), 'unicode-escape')
        except UnicodeDecodeError:
            # In case we matched the wrong thing after a double-backslash
            return match.group(0)

    return ESCAPE_SEQUENCE_RE.sub(decode_match, s)


"""
Overview of the process
1. Read TSV
2. Sanity Check
2a. Error Handling
3. Compile to JSON format

Maybe there will be configuration to sync typescript model with this converter
"""

VOLUME_DATA_LEN = 8
AUTHOR_DATA_LEN = 4
ARTICLE_DATA_LEN = 9

def parse_version(raw: list[str]):
    return raw[1]

def parse_volume_data(raw: list[str]):
    [_id, title,
     isbn, issn,
     publisher, published,
     pdf_link, cover_link] = raw[:VOLUME_DATA_LEN]
    return {
      'id': _id,
      'title': title,
      'publisher': publisher,
      'published': published,
      'ISBN': isbn,
      'ISSN': issn,
      'volumeLink': pdf_link,
      'coverLink': cover_link,
    }

def parse_authors_data(raw: list[str]):
    res = []
    while len(raw) > 0 and bool(raw[0].strip()):
        [name, surname, affiliation, orcid] = raw[:AUTHOR_DATA_LEN]
        author = { 'name': name.strip(),
                   'surname': surname.strip() }
        affiliation = affiliation.strip()
        if bool(affiliation):
            author['affiliation'] = affiliation
        orcid = orcid.strip()
        if bool(orcid):
            author['ORCID'] = orcid
        res.append(author)
        raw = raw[AUTHOR_DATA_LEN:]
    return res

def parse_article_data(raw: list[str]):
    [_id, title,
    page_range, doi,
    pdf_link, pdf_revised,
    abstract, note, keywords] = raw[:ARTICLE_DATA_LEN]
    partial_article = {
      'id': _id.strip(),
      'title': decode_escapes(title.strip()),
      'pageRange': page_range.strip(),
      'doi': doi.strip(),
      'pdfLink': pdf_link.strip()
    }
    abstract = abstract.strip()
    if bool(abstract):
        partial_article['abstract'] = abstract
    note = note.strip()
    if bool(note):
        partial_article['note'] = note
    keywords = keywords.strip()
    if bool(keywords):
        partial_article['keywords'] = keywords
    pdf_revised = pdf_revised.strip()
    if bool(pdf_revised):
        partial_article['pdfRevisedLink']
    partial_article['authors'] = parse_authors_data(raw[9:])
    return partial_article

def convert_data(raw: list[list[str]]):
    partial_volume = parse_volume_data(raw[2])
    partial_volume['articles'] = list(map(parse_article_data, raw[4:]))
    return partial_volume


def read_raw_data(filename: str) -> list[list[str]]:
    """Read Tab-Separated Value file"""
    with open(filename, newline='') as tsvfile:
        return list(x 
            for x in 
            csv.reader(
                tsvfile,
                delimiter='\t',
                quotechar='"'))

def write_json_data(filename: str, data: list[list[str]]) -> None:
    """Write JSON file for website"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False) # , indent=4)

def main() -> int:
    """Do stuff"""
    if len(sys.argv) < 2 or len(sys.argv) > 2:
        print(f"Usage: {sys.argv[0]} file_name.csv", file=sys.stderr)
        return 1
    input_file = sys.argv[1]
    raw_lines = read_raw_data(input_file)
    version = parse_version(raw_lines[0])
    if version != "10":
        print(f"Unsupported version {version}: "
            + f"this program works with version 10 only.",
            file=sys.stderr)
        return 1
    # TODO: if another argument is passed, that is the output file and we do
    # not print to stdout
    print(json.dumps(convert_data(raw_lines), ensure_ascii=False, indent=2))
    return 0

if __name__ == '__main__':
    sys.exit(main())

