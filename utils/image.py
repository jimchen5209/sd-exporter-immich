from sd_prompt_reader.image_data_reader import ImageDataReader
from lxml import etree


def read_image_metadata(image_path: str):
    with open(image_path, "rb+") as f:
        image_metadata = ImageDataReader(f)
        return image_metadata

def write_xmp(path: str, description: str, tags: list[str]):
    # XMP
    xmp = etree.Element("{adobe:ns:meta/}xmpmeta")
    rdf = etree.SubElement(xmp, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
    description_element = etree.SubElement(rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    
    # Description
    description_element.set("{http://purl.org/dc/elements/1.1/}description", description)
    
    # Tags
    tags_element = etree.SubElement(description_element, "{http://www.digikam.org/ns/1.0/}TagsList")
    for tag in tags:
        etree.SubElement(tags_element, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = tag

    # Save
    tree = etree.ElementTree(xmp)
    tree.write(path, encoding="utf-8", xml_declaration=True, pretty_print=True)
