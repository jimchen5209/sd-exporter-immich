# sd-exporter-immich

A tool to export images metadata from Stable Diffusion to [Immich](https://immich.app/) supported [XMP Sidecars](https://docs.immich.app/features/xmp-sidecars) format.

## Usage

1. Clone or download this repository.
2. Install dependencies:
  - With [uv](https://docs.astral.sh/uv/) (Recommended):
    ```bash
    uv sync
    ```
  - With pip:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the exporter:
    ```bash
    python main.py <path-to-your-images-directory>
    ```
    or with uv:
    ```bash
    uv run main.py <path-to-your-images-directory>
    ```
4. The XMP Sidecars will be generated alongside the images in the specified input directory.

## Upload to Immich

You need to upload the images alongside the generated XMP sidecar files with [Immich's CLI tool](https://docs.immich.app/features/command-line-interface).
You'll need an API key, required permissions: `asset.upload`, `user.read`.

Assume you have cli installed, and you haven't uploaded yet because immich will skip the existing images.
```bash
immich login <your-immich-url> <your-api-key>
immich upload --recursive <path-to-your-images-directory>
```
