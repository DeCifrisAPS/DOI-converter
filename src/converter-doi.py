#!/usr/bin/env python3
import os
import sys
import json
import requests
import datetime
import xml.etree.ElementTree as ET
import lxml.etree as LET

def test():
    message = ET.Element('ONIXDOISerialArticleWorkRegistrationMessage')
    message.attrib['xmlns'] = 'http://www.editeur.org/onix/DOIMetadata/2.0'
    # message.attrib['xmlns'] = 'http://www.medra.org/schema/onix/DOIMetadata/2.0/ONIX_DOIMetadata_2.0.xsd'
    message.attrib['xmlns:xsi'] = 'http://www.w3.org/2001/XMLSchema-instance'
    message.attrib['xmlns:cl'] = 'http://www.medra.org/DOIMetadata/2.0/Citations'
    message.attrib['xsi:schemaLocation'] = 'http://www.editeur.org/onix/DOIMetadata/2.0 http://www.medra.org/schema/onix/DOIMetadata/2.0/ONIX_DOIMetadata_2.0.xsd'
    root = ET.ElementTree(message)

    header = ET.SubElement(message, 'Header')
    from_company = ET.SubElement(header, 'FromCompany')
    from_company.text = 'De Componendis Cifris APS'

    from_email = ET.SubElement(header, 'FromEmail')
    from_email.text = 'editorial@decifris.it'

    to_company = ET.SubElement(header, 'ToCompany')
    to_company.text = 'mEDRA'

    sent_date = ET.SubElement(header, 'SentDate')
    sent_date.text = datetime.datetime.now().strftime('%Y%m%d%H%M')

    # message.append(header)

    # Begin for each DOI
    work = ET.SubElement(message, 'DOISerialArticleWork')

    notification_type = ET.SubElement(work, 'NotificationType')
    notification_type.text = '06' # 06 creation, 07 update

    doi = ET.SubElement(work, 'DOI')
    doi.text = '10.69091/koine/vol-3-I01'

    doi_website = ET.SubElement(work, 'DOIWebsiteLink')
    doi_website.text = 'https://decifris.it/koine/vol3/I01'

    registrant_name = ET.SubElement(work, 'RegistrantName')
    registrant_name.text = 'De Componendir Cifris APS'

    registration_authority = ET.SubElement(work, 'RegistrationAuthority')
    registration_authority.text = 'mEDRA'

    serial_publication = ET.SubElement(work, 'SerialPublication')

    serial_work = ET.SubElement(serial_publication, 'SerialWork')
    
    work_title = ET.SubElement(serial_work, 'Title')
    
    title_type = ET.SubElement(work_title, 'TitleType')
    title_type.text = '01' # Distinctive title (05 abbreviated)

    title_type = ET.SubElement(work_title, 'TitleText')
    title_type.text = 'ERUDITORUM ACTA 2024'

    # TODO: ISSN
    # TODO: Nome rivista?

    # Formato del prodotto: rivista stampata

    publisher = ET.SubElement(serial_work, 'Publisher')

    publisher_role = ET.SubElement(publisher, 'PublishingRole')
    publisher_role.text = '01' # Publisher (02 - co-publisher) (05 abbreviated)

    publisher_name = ET.SubElement(publisher, 'PublisherName')
    publisher_name.text = 'De Cifris Press'

    country_of_publication = ET.SubElement(serial_work, 'CountryOfPublication')
    country_of_publication.text = 'IT'

    journal_issue = ET.SubElement(work, 'JournalIssue')

    issue_number = ET.SubElement(journal_issue, 'JournalIssueNumber')
    issue_number.text = '3'

    # TODO: Journal Issue Designation?
    # TODO: Journal Issue Date?

    content_item = ET.SubElement(work, 'ContentItem')

    content_title = ET.SubElement(content_item, 'Title')

    content_title_type = ET.SubElement(content_title, 'TitleType')
    content_title_type.text = '01'

    content_title_text = ET.SubElement(content_title, 'TitleText')
    content_title_text.text = 'Introduzione a De Cifris Eruditorum'


    # TODO: language
    # TODO: author
    # TODO: page range, number
    



    message_str = ET.tostring(message)
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
