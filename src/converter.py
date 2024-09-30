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


VOLUME_ROW = 2
ARTICLE_START_ROW = 4
VOLUME_DATA_LEN = 8
AUTHOR_DATA_LEN = 4
ARTICLE_DATA_LEN = 9

class ParserV10():
    def __parse_version(self, raw: list[str]):
        return raw[1]

    def __parse_volume_data(self, raw: list[str]):
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

    def __parse_authors_data(self, raw: list[str]):
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

    def __parse_article_data(self, raw: list[str]):
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
            partial_article['pdfRevisedLink'] = pdf_revised
        partial_article['authors'] = self.__parse_authors_data(raw[ARTICLE_DATA_LEN:])
        return partial_article

    def convert_data(self, raw: list[list[str]]):
        partial_volume = self.__parse_volume_data(raw[VOLUME_ROW])
        partial_volume['articles'] = list(map(
                                            self.__parse_article_data,
                                            raw[ARTICLE_START_ROW:]))
        return partial_volume

    def __count_first_non_empty(line: [str], after: int = 0) -> int:
        c = after
        while c < len(line) and bool(line[c]):
            c += 1
        return c

    def sanity_check(self, raw_lines: list[list[str]]) -> bool:
        if len(raw_lines) < 5:
            return False, ["File contains less than five rows"]
        # Check version
        if len(raw_lines[0]) < 2:
            return False, ["First line does not contain the version column."]
        version = self.__parse_version(raw_lines[0])
        if version != "10":
            return False, [f"Unsupported version {version}: "
                + f"this program works with version 10 only."]
        sane = True
        error_messages = []
        # Volume section
        if len(raw_lines[2]) != VOLUME_DATA_LEN:
            sane = False
            error_messages.append(f"Volume section is incorrect."
                + f" Expected {VOLUME_DATA_LEN} elements."
                + f" Found {len(raw_lines[2])} elements.")
        # Article section
        # for line_number in range(ARTICLE_START_ROW, len(raw_lines)):
        line_length = len(raw_lines[ARTICLE_START_ROW])
        if line_length < ARTICLE_DATA_LEN + AUTHOR_DATA_LEN:
            error_messages.append(f"Article lines are incorrect."
                + f" Expected {ARTICLE_DATA_LEN + AUTHOR_DATA_LEN} elements."
                + f" Found {line_length} elements.")
            sane = False
        elif (line_length - ARTICLE_DATA_LEN) % AUTHOR_DATA_LEN != 0:
            maybe_authors = max(1,
                            (line_length - ARTICLE_DATA_LEN) // AUTHOR_DATA_LEN)
            expected_min = ARTICLE_DATA_LEN + AUTHOR_DATA_LEN * maybe_authors
            expected_max = ARTICLE_DATA_LEN + AUTHOR_DATA_LEN * (maybe_authors + 1)
            error_messages.append(f"Article lines are incorrect."
                + f" Expected {expected_max} or {expected_min} elements."
                + f" Found {line_length} elements.")
            sane = False
            # This check is noisy and applied to the whole document
            # break
        return sane, error_messages

def read_raw_data(filename: str) -> list[list[str]]:
    """Read Tab-Separated Value file"""
    with open(filename, newline='') as tsvfile:
        return list(x for x in 
            csv.reader(tsvfile, delimiter='\t', quotechar='"'))

def main() -> int:
    """
    Overview of the process
        1. Read TSV
        2. Sanity Check
        2a. Error Handling
        3. Compile to JSON format
    Maybe there will be configuration to sync typescript model with this converter
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} file_name.csv", file=sys.stderr)
        return 1
    input_file = sys.argv[1]
    raw_lines = read_raw_data(input_file)
    parser = None
    if len(raw_lines) > 0 and len(raw_lines[0]) >= 2 and raw_lines[0][1] == "10":
        parser = ParserV10()
    else:
        print(f"Unsupported version: this program works with version 10 only.",
                file=sys.stderr)
        return 1
    ok, error_messages = parser.sanity_check(raw_lines)
    if not ok:
        print('\n'.join(error_messages), file=sys.stderr)
        return 1
    if len(sys.argv) == 2:
        print(f"File OK", file=sys.stderr)
        return 0
    output_file = sys.argv[2]
    converted = parser.convert_data(raw_lines)
    if output_file == "-":
        print(json.dumps(converted, ensure_ascii=False, indent=2))
    else:
        with open(output_file, "w") as ofile:
            json.dump(converted, ofile, ensure_ascii=False)
    return 0

if __name__ == '__main__':
    sys.exit(main())

