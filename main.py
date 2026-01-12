import argparse
import os
from sd_prompt_reader.image_data_reader import ImageDataReader
from sd_prompt_reader.constants import SUPPORTED_FORMATS
from tqdm import tqdm
from lxml import etree

def read_image_metadata(image_path):
    with open(image_path, "rb+") as f:
        image_metadata = ImageDataReader(f)
        return image_metadata

def create_xmp(xmp_path, positive, negative, settings):
    # XMP
    xmp = etree.Element("{adobe:ns:meta/}xmpmeta")
    rdf = etree.SubElement(xmp, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
    desc = etree.SubElement(rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    
    # Description
    desc.set("{http://purl.org/dc/elements/1.1/}description", positive)
    
    # Tags
    tags = etree.SubElement(desc, "{http://www.digikam.org/ns/1.0/}TagsList")
    etree.SubElement(tags, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = f"Negative: {negative}"
    splitted_settings = settings.split(", ")
    for setting in splitted_settings:
        etree.SubElement(tags, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = setting
    
    # Save
    tree = etree.ElementTree(xmp)
    tree.write(xmp_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

def main():
    parser = argparse.ArgumentParser(description="Read metadata")
    parser.add_argument("input_dir", help="input")
    args = parser.parse_args()

    input_dir = args.input_dir

    if not os.path.exists(input_dir):
        raise ValueError(f"Input directory {input_dir} does not exist.")

    generated = []
    existed = []
    unsupported = []

    files = os.listdir(input_dir)
    for file in tqdm(files, "Processing files", unit=" file"):
        ext = os.path.splitext(file)[1].lower()
        if not ext in SUPPORTED_FORMATS:
            if ext != ".xmp":
                unsupported.append(file)
            continue

        file_path = os.path.join(input_dir, file)
        output_path = os.path.join(input_dir, os.path.basename(file_path).split(".")[0] + ".xmp")

        if os.path.exists(output_path):
            existed.append(file)
            continue

        image_metadata = read_image_metadata(file_path)
        create_xmp(output_path, image_metadata.positive, image_metadata.negative, image_metadata.setting)
        generated.append(file)

    print(f"Generated: {len(generated)} Existed: {len(existed)} Unsupported: {len(unsupported)}")

if __name__ == "__main__":
    main()
