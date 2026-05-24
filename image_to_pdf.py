#!/usr/bin/env python3
"""Convert image files or folders of images into PDF files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:  # pragma: no cover - shown only when Pillow is missing.
    print(
        "Pillow belum terpasang. Jalankan: python -m pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(1)


SUPPORTED_EXTENSIONS = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def collect_images(inputs: list[Path], recursive: bool) -> list[Path]:
    images: list[Path] = []

    for input_path in inputs:
        path = input_path.expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Tidak ditemukan: {input_path}")

        if path.is_file():
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise ValueError(f"Bukan file gambar yang didukung: {input_path}")
            images.append(path)
            continue

        pattern = "**/*" if recursive else "*"
        images.extend(
            sorted(
                child
                for child in path.glob(pattern)
                if child.is_file() and child.suffix.lower() in SUPPORTED_EXTENSIONS
            )
        )

    if not images:
        raise ValueError("Tidak ada gambar yang bisa dikonversi.")

    return sorted(dict.fromkeys(images))


def load_image(path: Path) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image)

    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        background = Image.new("RGB", image.size, "white")
        alpha = image.convert("RGBA").getchannel("A")
        background.paste(image.convert("RGB"), mask=alpha)
        return background

    return image.convert("RGB")


def convert_images_to_pdf(images: list[Path], output: Path) -> None:
    first_image, *remaining_images = [load_image(path) for path in images]

    output.parent.mkdir(parents=True, exist_ok=True)
    first_image.save(
        output,
        "PDF",
        resolution=100.0,
        save_all=True,
        append_images=remaining_images,
    )

    first_image.close()
    for image in remaining_images:
        image.close()


def default_output_path(images: list[Path]) -> Path:
    if len(images) == 1:
        return images[0].with_suffix(".pdf")
    return Path.cwd() / "converted-images.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert image files or folders of images into a single PDF."
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        type=Path,
        help="File gambar atau folder berisi gambar.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path PDF hasil. Default: nama gambar.pdf atau converted-images.pdf.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Ambil gambar dari subfolder juga.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        images = collect_images(args.inputs, args.recursive)
        output = (args.output or default_output_path(images)).expanduser().resolve()
        convert_images_to_pdf(images, output)
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Berhasil membuat PDF: {output}")
    print(f"Total gambar: {len(images)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
