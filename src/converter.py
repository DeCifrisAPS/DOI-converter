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


def parse_version(raw: list[str]):
    return raw[1]


VOLUME_DATA_LEN = 8

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


AUTHOR_DATA_LEN = 4

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


ARTICLE_DATA_LEN = 9

def parse_article_data(raw: list[str]):
    [_id, title,
    page_range, doi,
    pdf_link, pdf_revised,
    abstract, note, keywords] = raw[:ARTICLE_DATA_LEN]
    partial_article = {
      'id': _id.strip(),
      'title': title.strip(),
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
        return list(x for x in csv.reader(tsvfile, delimiter='\t', quotechar='"'))

def write_json_data(filename: str, data: list[list[str]]) -> None:
    """Write JSON file for website"""
    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, ensure_ascii=False) # , indent=4)

def main() -> int:
    """Do stuff"""
    raw_lines = read_raw_data('../examples/vol3.csv')
    print(parse_version(raw_lines[0]))
    # print(parse_volume_data(raw_lines[2]))
    # print(parse_article_data(raw_lines[4]))
    print(convert_data(raw_lines))
    return 0

if __name__ == '__main__':
    sys.exit(main())

