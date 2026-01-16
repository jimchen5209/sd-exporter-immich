import argparse
import os
from pathlib import Path
from sd_prompt_reader.constants import SUPPORTED_FORMATS
from tqdm import tqdm

from utils.image import read_image_metadata, write_xmp
from utils.parser import parse_settings, parse_tag


def process(path: Path):
    generated = []
    existed = []
    unsupported = []

    files = os.listdir(path)
    for file in tqdm(files, "Processing files", unit=" file"):
        ext = os.path.splitext(file)[1].lower()
        if not ext in SUPPORTED_FORMATS:
            if ext != ".xmp":
                unsupported.append(file)
            continue

        file_path = path / file
        output_path = file_path.with_suffix(".xmp")

        if os.path.exists(output_path):
            existed.append(file)
            continue

        image_metadata = read_image_metadata(file_path)
        convert_to_xmp(output_path, image_metadata.positive, image_metadata.negative, image_metadata.setting)
        generated.append(file)

    print(f"Generated: {len(generated)} Existed: {len(existed)} Unsupported: {len(unsupported)}")

def convert_to_xmp(xmp_path: str, positive: str, negative: str, settings: str):
    # Description
    parsed_settings = parse_settings(settings)
    settings_str = '\n'.join([f"{key}: {value}" for key, value in parsed_settings.items()])
    description= f"Prompt: {positive}\nNegative: {negative}\n{settings_str}"
    
    # Tags
    parsed_tags = parse_tag(positive)
    
    # Save
    write_xmp(xmp_path, description, parsed_tags)

def main():
    parser = argparse.ArgumentParser(description="Read metadata")
    parser.add_argument("input_dir", help="input")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)

    if not input_dir.exists():
        parser.error(f"Image folder '{input_dir}' does not exist.")

    if not input_dir.is_dir():
        parser.error(f"'{input_dir}' is not a folder.")

    process(input_dir)

if __name__ == "__main__":
    main()
