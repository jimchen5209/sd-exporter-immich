from sd_prompt_reader.image_data_reader import ImageDataReader
from lxml import etree


def read_image_metadata(image_path: str):
    with open(image_path, "rb+") as f:
        image_metadata = ImageDataReader(f)
        return image_metadata

def write_xmp(path: str, description: str, tags: list[str]):
    # Define namespaces as constants to improve readability and maintainability.
    NS_ADOBE_META = "{adobe:ns:meta/}"
    NS_RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
    NS_DC = "{http://purl.org/dc/elements/1.1/}"
    NS_DIGIKAM = "{http://www.digikam.org/ns/1.0/}"

    # XMP
    xmp = etree.Element(f"{NS_ADOBE_META}xmpmeta")
    rdf = etree.SubElement(xmp, f"{NS_RDF}RDF")
    description_element = etree.SubElement(rdf, f"{NS_RDF}Description")
    
    # Description
    description_element.set(f"{NS_DC}description", description)
    
    # Tags
    tags_element = etree.SubElement(description_element, f"{NS_DIGIKAM}TagsList")
    for tag in tags:
        etree.SubElement(tags_element, f"{NS_RDF}li").text = tag

    # Save
    tree = etree.ElementTree(xmp)
    tree.write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)
