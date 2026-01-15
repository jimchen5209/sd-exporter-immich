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

def parse_tag(tag):
    return tag.strip() \
        .replace("\\(", "<bracket>") \
        .replace("\\)", "</bracket>") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("<bracket>", "(")  \
        .replace("</bracket>", ")") \
        .replace("\\[", "<square>") \
        .replace("\\]", "</square>") \
        .replace("[", "") \
        .replace("]", "") \
        .replace("<square>", "[")  \
        .replace("</square>", "]") \
        .replace("\\{", "<curly>") \
        .replace("\\}", "</curly>") \
        .replace("{", "") \
        .replace("}", "") \
        .replace("<curly>", "{")  \
        .replace("</curly>", "}")

def create_xmp(xmp_path, positive, negative, settings):
    # XMP
    xmp = etree.Element("{adobe:ns:meta/}xmpmeta")
    rdf = etree.SubElement(xmp, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
    desc = etree.SubElement(rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description")
    
    # Description
    settings = "\n".join(settings.split(", "))
    description= f"Prompt: {positive}\nNegative: {negative}\n{settings}"
    desc.set("{http://purl.org/dc/elements/1.1/}description", description)
    
    # Tags
    tags = etree.SubElement(desc, "{http://www.digikam.org/ns/1.0/}TagsList")
    splitted_prompt = map(parse_tag, positive.split(","))
    for prompt in splitted_prompt:
        etree.SubElement(tags, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li").text = prompt
    
    # Save
    tree = etree.ElementTree(xmp)
    tree.write(xmp_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

def main():
    supported_formats_text = ", ".join(SUPPORTED_FORMATS)
    parser = argparse.ArgumentParser(description=f"Convert Stable Diffusion metadata from {supported_formats_text} files to immich supported .xmp files.")
    parser.add_argument("image_folder", help="Folder containing images to convert from.")
    args = parser.parse_args()

    image_folder = args.image_folder

    if not os.path.exists(image_folder):
        raise ValueError(f"Input directory {image_folder} does not exist.")

    generated = []
    existed = []
    unsupported = []

    files = os.listdir(image_folder)
    for file in tqdm(files, "Processing files", unit=" file"):
        ext = os.path.splitext(file)[1].lower()
        if not ext in SUPPORTED_FORMATS:
            if ext != ".xmp":
                unsupported.append(file)
            continue

        file_path = os.path.join(image_folder, file)
        output_path = os.path.join(image_folder, os.path.basename(file_path).split(".")[0] + ".xmp")

        if os.path.exists(output_path):
            existed.append(file)
            continue

        image_metadata = read_image_metadata(file_path)
        create_xmp(output_path, image_metadata.positive, image_metadata.negative, image_metadata.setting)
        generated.append(file)

    print(f"Generated: {len(generated)} Existed: {len(existed)} Unsupported: {len(unsupported)}")

if __name__ == "__main__":
    main()
