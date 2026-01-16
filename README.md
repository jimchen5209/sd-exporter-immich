# sd-exporter-immich

A tool to export images metadata from Stable Diffusion to [Immich](https://immich.app/) supported [XMP Sidecars](https://docs.immich.app/features/xmp-sidecars) format.

> [!NOTE]
> Tag parsing in this tool is designed for [sdnext](https://vladmandic.github.io/sdnext-docs/).

## Usage

1. Install this package with pip or [pipx](https://github.com/pypa/pipx) (Recommend using pipx):
    ```bash
    pip install git+https://github.com/jimchen5209/sd-exporter-immich.git
    ```
    or
    ```bash
    pipx install git+https://github.com/jimchen5209/sd-exporter-immich.git
    ```
2. Run the exporter:
    ```bash
    sd-export <path-to-your-images-directory>
    ```
3. The XMP Sidecars will be generated alongside the images in the specified input directory.

## Uninstall
To uninstall, run:
```bash
  pip uninstall sd-exporter-immich
```
or
```bash
  pipx uninstall sd-exporter-immich
```

## Upload to Immich

You need to upload the images alongside the generated XMP sidecar files with [Immich's CLI tool](https://docs.immich.app/features/command-line-interface).
You'll need an API key, required permissions: `asset.upload`, `user.read`.

Assume you have cli installed, and you haven't uploaded yet because immich will skip the existing images.
```bash
immich login <your-immich-url> <your-api-key>
immich upload --recursive <path-to-your-images-directory>
```

## Development

1. Clone or download this repository.
2. Install dependencies with [uv](https://docs.astral.sh/uv/):
    ```bash
    uv sync
    ```
3. Run:
    ```bash
    uv run sd-export <path-to-your-images-directory>
    ```
