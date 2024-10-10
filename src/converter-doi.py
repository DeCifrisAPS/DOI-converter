#!/usr/bin/env python3
import os
import sys
import json
import requests
import datetime
import xml.etree.ElementTree as ET
import lxml.etree as LET

def create_header(message):
    header = ET.SubElement(message, 'Header')
    from_company = ET.SubElement(header, 'FromCompany')
    from_company.text = 'De Componendis Cifris APS'

    from_email = ET.SubElement(header, 'FromEmail')
    from_email.text = 'editorial@decifris.it'

    to_company = ET.SubElement(header, 'ToCompany')
    to_company.text = 'mEDRA RA'

    sent_date = ET.SubElement(header, 'SentDate')
    sent_date.text = datetime.datetime.now().strftime('%Y%m%d%H%M')

def add_title(elt, title, language):
    work_title = ET.SubElement(elt, 'Title')
    work_title.attrib['language'] = language

    title_type = ET.SubElement(work_title, 'TitleType')
    title_type.text = '01' # Distinctive title (05 abbreviated)

    title_type = ET.SubElement(work_title, 'TitleText')
    title_type.text = title

def add_language(elt, lang):
    language = ET.SubElement(elt, 'Language')

    language_role = ET.SubElement(language, 'LanguageRole')
    language_role.text = '01'

    language_code = ET.SubElement(language, 'LanguageCode')
    language_code.text = lang

def add_page_ranges(elt, rng):
    fst = rng.split('-')[0]
    snd = rng.split('-')[1]
    tot = str(int(snd) - int(fst) + 1)
    text_item = ET.SubElement(elt, 'TextItem')

    page_run = ET.SubElement(text_item, 'PageRun')
    
    first_page = ET.SubElement(page_run, 'FirstPageNumber')
    first_page.text = fst

    last_page = ET.SubElement(page_run, 'LastPageNumber')
    last_page.text = snd

    number_of_pages = ET.SubElement(text_item, 'NumberOfPages')
    number_of_pages.text = tot

def add_author(elt, idx, name, surname, affiliation):
    contributor = ET.SubElement(elt, 'Contributor')

    sequence_number = ET.SubElement(contributor, 'SequenceNumber')
    sequence_number.text = str(idx)

    contributor_role = ET.SubElement(contributor, 'ContributorRole')
    contributor_role.text = 'A01'
    
    person_name = ET.SubElement(contributor, 'PersonName')
    person_name.text = name + ' ' + surname

    person_name_inverted = ET.SubElement(contributor, 'PersonNameInverted')
    person_name_inverted.text = surname + ', ' + name

    name_before_key = ET.SubElement(contributor, 'NamesBeforeKey')
    name_before_key.text = name

    key_names = ET.SubElement(contributor, 'KeyNames')
    key_names.text = surname

    professional_affiliation = ET.SubElement(contributor, 'ProfessionalAffiliation')
    affiliation_tag = ET.SubElement(professional_affiliation, 'Affiliation')
    affiliation_tag.text = affiliation


def append_work(message):
    # Begin for each DOI
    work = ET.SubElement(message, 'DOISerialArticleWork')

    notification_type = ET.SubElement(work, 'NotificationType')
    notification_type.text = '06' # 06 creation, 07 update

    doi = ET.SubElement(work, 'DOI')
    doi.text = '10.69091/koine/vol-2-T04'

    doi_website = ET.SubElement(work, 'DOIWebsiteLink')
    doi_website.text = 'https://decifris.it/koine/vol2/T04'

    access_indicators = ET.SubElement(work, 'AccessIndicators')
    ET.SubElement(access_indicators, 'FreeToRead')

    registrant_name = ET.SubElement(work, 'RegistrantName')
    registrant_name.text = 'De Componendis Cifris APS'

    registration_authority = ET.SubElement(work, 'RegistrationAuthority')
    registration_authority.text = 'mEDRA'

    serial_publication = ET.SubElement(work, 'SerialPublication')

    serial_work = ET.SubElement(serial_publication, 'SerialWork')
    
    # work_identifier = ET.SubElement(serial_work, 'WorkIdentifier')

    # work_id_type = ET.SubElement(work_identifier, 'WorkIDType')
    # work_id_type.text = '08' # CODEN

    # id_value = ET.SubElement(work_identifier, 'IDValue')
    # id_value.text = '3034-9796' # ISSN

    add_title(serial_work, 'De Cifris Koine', 'eng')

    publisher = ET.SubElement(serial_work, 'Publisher')

    publisher_role = ET.SubElement(publisher, 'PublishingRole')
    publisher_role.text = '01' # Publisher (02 - co-publisher) (05 abbreviated)

    publisher_name = ET.SubElement(publisher, 'PublisherName')
    publisher_name.text = 'De Componendis Cifris APS'

    country_of_publication = ET.SubElement(serial_work, 'CountryOfPublication')
    country_of_publication.text = 'IT'

    serial_version = ET.SubElement(serial_publication, 'SerialVersion')
    product_identifier = ET.SubElement(serial_version, 'ProductIdentifier')
    product_id_type = ET.SubElement(product_identifier, 'ProductIDType')
    product_id_type.text = '07'
    product_id_value = ET.SubElement(product_identifier, 'IDValue')
    product_id_value.text = '3034-9796'
    product_form = ET.SubElement(serial_version, 'ProductForm')
    product_form.text = 'JB' # Rivista stampata

    journal_issue = ET.SubElement(work, 'JournalIssue')
    issue_number = ET.SubElement(journal_issue, 'JournalIssueNumber')
    issue_number.text = '2'
    journal_issue_date = ET.SubElement(journal_issue, 'JournalIssueDate')
    date_format = ET.SubElement(journal_issue_date, 'DateFormat')
    date_format.text = '00'
    date_issue = ET.SubElement(journal_issue_date, 'Date')
    date_issue.text = datetime.datetime.now().strftime('%Y%m%d')

    content_item = ET.SubElement(work, 'ContentItem')
    add_page_ranges(content_item, '17-20')
    add_title(content_item, 'On adapting NTRU for Post-Quantum Public-Key Encryption', 'eng')
    add_author(content_item, 1, 'Simone', 'Dutto', 'Politecnico di Torino')
    add_author(content_item, 2, 'Gugliemino', 'Morgani', 'Telsy Spa')
    add_author(content_item, 3, 'Edoardo', 'Signorini', 'Politecnico di Torino e Telsy Spa')
    add_language(content_item, 'eng')
    publication_date = ET.SubElement(content_item, 'PublicationDate')
    publication_date.text = datetime.datetime.now().strftime('%Y%m%d')

def test():
    message = ET.Element('ONIXDOISerialArticleWorkRegistrationMessage')
    message.attrib['xmlns'] = 'http://www.editeur.org/onix/DOIMetadata/2.0'
    # message.attrib['xmlns'] = 'http://www.medra.org/schema/onix/DOIMetadata/2.0/ONIX_DOIMetadata_2.0.xsd'
    message.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    message.attrib['xmlns:cl'] = 'http://www.medra.org/DOIMetadata/2.0/Citations'
    message.attrib['xsi:schemaLocation'] = 'http://www.editeur.org/onix/DOIMetadata/2.0 http://www.medra.org/schema/onix/DOIMetadata/2.0/ONIX_DOIMetadata_2.0.xsd'
    root = ET.ElementTree(message)

    create_header(message)
    # TODO: for each DOI do
    append_work(message)

    ET.indent(message)
    message_str = ET.tostring(message, encoding='unicode')
    print(message_str)
    schema_root = ''
    with open('./ONIX_DOIMetadata_2.0.xsd', 'rb') as f:
        schema_root = LET.XML(f.read())
    schema = LET.XMLSchema(schema_root)
    parser = LET.XMLParser(schema = schema)
    _r = LET.fromstring(message_str, parser)
    # # print(ET.tostring(message, encoding='utf-8'))
    with open('text.xml', 'w', encoding='utf-8') as f:
        root.write(f,
                    encoding='unicode')
                    #default_namespace='http://www.editeur.org/onix/DOIMetadata/2.0')
    # parser = LET.XMLParser(dtd_validation=True)
    # print(ET.tostring(message))
    print(_r)

    print("OK")

def convert_json_to_doi_data(collana: str, json_data: dict) -> (bool, [str]):
    print(json_data)
    print(collana)
    return False, ["Did nothing"]

def read_json_file(filename: str) -> dict:
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def main() -> int:
    """
    Convert site JSON to DOI XML
    """
    if len(sys.argv) < 3 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} file_name.json nome_collana", file=sys.stderr)
        return 1
    filename = sys.argv[1]
    collana = sys.argv[2]
    # read json file(?)
    # run for each article the DOI creation
    json_data = read_json_file(filename)
    ok, error_message = convert_json_to_doi_data(collana, json_data)
    if not ok:
        print('\n'.join(error_message), file=sys.stderr)

if __name__ == '__main__':
    test()
    # sys.exit(main())
