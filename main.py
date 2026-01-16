import argparse
import os
from pathlib import Path
from sd_prompt_reader.constants import SUPPORTED_FORMATS
from tqdm import tqdm

from utils.image import read_image_metadata, write_xmp
from utils.parser import parse_settings, parse_tag

def validate_file_path(canonical_input_dir: Path, file_path_raw: Path) -> Path | None:
    try:
        # Resolve each file path to handle symlinks or other traversal attempts within the directory
        canonical_file_path = file_path_raw.resolve(strict=True)
    except FileNotFoundError:
        print(f"Warning: File '{file_path_raw}' not found or inaccessible, skipping.")
        return None
    except Exception as e:
        print(f"Warning: Could not resolve path for '{file_path_raw}': {e}, skipping.")
        return None
    # CRITICAL: Validate that the resolved file path is still within the canonical input directory
    if not canonical_file_path.is_relative_to(canonical_input_dir):
        print(f"Security Alert: Path traversal attempt detected for '{file_path_raw}', skipping.")
        return None
    # Now, `file_path` holds the safe, resolved path to the file.
    # Subsequent code (e.g., for output_path) should use this resolved file_path.
    return canonical_file_path

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

        file_path = validate_file_path(path, path / file)
        if file_path is None:
            continue
        output_path = file_path.with_suffix(".xmp")

        if os.path.exists(output_path):
            existed.append(file)
            continue

        image_metadata = read_image_metadata(file_path)
        convert_to_xmp(output_path, image_metadata.positive, image_metadata.negative, image_metadata.setting)
        generated.append(file)

    print(f"Generated: {len(generated)} Existed: {len(existed)} Unsupported: {len(unsupported)}")

def convert_to_xmp(xmp_path: Path, positive: str, negative: str, settings: str):
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

    # Convert input path to Path object and resolve it
    try:
        canonical_input_dir = input_dir.resolve(strict=True)
    except FileNotFoundError:
        # Consistent with main's ValueError for non-existent directory
        parser.error(f"Image folder '{input_dir}' does not exist.")
    except Exception as e:
        # Catch other resolution errors
        parser.error(f"Invalid image folder '{input_dir}': {e}")

    if not canonical_input_dir.is_dir():
        parser.error(f"'{input_dir}' is not a folder.")

    print(f"Image folder: {canonical_input_dir}")

    process(canonical_input_dir)

if __name__ == "__main__":
    main()
