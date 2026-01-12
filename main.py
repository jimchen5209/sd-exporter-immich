import argparse
from sd_prompt_reader.image_data_reader import ImageDataReader

def read_image_metadata(image_path):
    with open(image_path, "rb+") as f:
        image_metadata = ImageDataReader(f)
        return image_metadata


def main():
    parser = argparse.ArgumentParser(description="Read metadata")
    parser.add_argument("input_file1", help="input")
    args = parser.parse_args()

    input_1 = args.input_file1

    image_metadata = read_image_metadata(input_1)
    if image_metadata.status.name == "READ_SUCCESS":
        print("Positive: ", image_metadata.positive)
        print("Negative: ", image_metadata.negative)
        print("Setting: ", image_metadata.setting)
    else:
        print(f"Reading Status: {image_metadata.status.name}")


if __name__ == "__main__":
    main()
