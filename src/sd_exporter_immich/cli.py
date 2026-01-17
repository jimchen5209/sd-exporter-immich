import argparse
from dataclasses import dataclass
from pathlib import Path
from sd_prompt_reader.constants import SUPPORTED_FORMATS  # pyright: ignore[reportMissingTypeStubs]
from tqdm import tqdm

from sd_exporter_immich.utils.image import read_image_metadata, write_xmp
from sd_exporter_immich.utils.parser import parse_settings, parse_tag


@dataclass
class ProgramArgs:
    image_folder: str


def validate_file_path(canonical_input_dir: Path, file_path_raw: Path) -> Path | None:
    try:
        # Resolve each file path to handle symlinks or other traversal attempts within the directory
        canonical_file_path = file_path_raw.resolve(strict=True)
    except FileNotFoundError:
        print(f"Warning: File '{file_path_raw}' not found or inaccessible, skipping.")
        return None
    except (OSError, RuntimeError) as e:
        print(f"Warning: Could not resolve path for '{file_path_raw}': {e}, skipping.")
        return None
    # CRITICAL: Validate that the resolved file path is still within the canonical input directory
    if not canonical_file_path.is_relative_to(canonical_input_dir):
        print(
            f"Security Alert: Path traversal attempt detected for '{file_path_raw}', skipping."
        )
        return None
    # Now, `file_path` holds the safe, resolved path to the file.
    # Subsequent code (e.g., for output_path) should use this resolved file_path.
    return canonical_file_path


def process(path: Path):
    generated: list[str] = []
    existed: list[str] = []
    unsupported: list[str] = []

    for file in tqdm(list(path.iterdir()), "Processing files", unit=" file"):
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        if ext not in SUPPORTED_FORMATS:
            if ext != ".xmp":
                unsupported.append(file.name)
            continue

        file_path = validate_file_path(path, file)
        if file_path is None:
            continue
        output_path = file_path.with_suffix(".xmp")

        if output_path.exists():
            existed.append(file.name)
            continue

        image_metadata = read_image_metadata(file_path)
        convert_to_xmp(
            output_path,
            image_metadata.positive,
            image_metadata.negative,
            image_metadata.setting,
        )
        generated.append(file.name)

    print(
        f"Generated: {len(generated)} Existed: {len(existed)} Unsupported: {len(unsupported)}"
    )


def convert_to_xmp(xmp_path: Path, positive: str, negative: str, settings: str):
    # Description
    parsed_settings = parse_settings(settings)
    settings_str = "\n".join(
        [f"{key}: {value}" for key, value in parsed_settings.items()]
    )
    description = f"Prompt: {positive}\nNegative: {negative}\n{settings_str}"

    # Tags
    parsed_tags = parse_tag(positive)

    # Save
    write_xmp(xmp_path, description, parsed_tags)


def main():
    supported_formats_text = ", ".join(SUPPORTED_FORMATS)
    parser = argparse.ArgumentParser(
        description=f"Convert Stable Diffusion metadata from {supported_formats_text} files to immich supported .xmp files."
    )
    parser.add_argument(
        "image_folder", help="Folder containing images to convert from.", type=str
    )
    args = parser.parse_args(namespace=ProgramArgs)

    image_folder = Path(args.image_folder)

    # Convert input path to Path object and resolve it
    try:
        canonical_image_folder = image_folder.resolve(strict=True)
    except FileNotFoundError:
        # Consistent with main's ValueError for non-existent directory
        parser.error(f"Image folder '{image_folder}' does not exist.")
    except (OSError, RuntimeError) as e:
        # Catch other resolution errors
        parser.error(f"Invalid image folder '{image_folder}': {e}")

    if not canonical_image_folder.is_dir():
        parser.error(f"'{image_folder}' is not a folder.")

    print(f"Image folder: {canonical_image_folder}")

    process(canonical_image_folder)


if __name__ == "__main__":
    main()
