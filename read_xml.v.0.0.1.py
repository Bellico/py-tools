import os
import sys
import xml.etree.ElementTree as ET

XML_FILE = r"D:\Downloads\\test.xml"

if not os.path.exists(XML_FILE):
    print(XML_FILE, "not found")
    sys.exit()

tree = ET.parse(XML_FILE)
root = tree.getroot()

for annotation in root.find('IndividualPorosity').findall('Annotation'):
    id = annotation.get('id')
    diamater = annotation.get('diamater')
    volume = annotation.get('volume')
    print(id, diamater, volume)
