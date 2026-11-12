#!/usr/bin/env python3
"""
generate_qrcode.py

Generate a QR code image pointing to a Journal of Digital History
article page, given its pid.

Requirements:
    pip install qrcode[pil]

Usage:
    python generate_qrcode.py    (if script is included in article repository)
    python generate_qrcode.py 12345
    python generate_qrcode.py 12345 -o qrcode.png
    python generate_qrcode.py 12345 --base-url https://journalofdigitalhistory.org --lang en
"""

import argparse
import logging
import sys
from pathlib import Path

import qrcode
from get_pid import get_pid_from_repo
from PIL import Image
from qrcode.image.styledpil import StyledPilImage

LOGO_PATH = Path(__file__).parent / "jdh_logo_onwhitebg_rec.png"

logger = logging.getLogger(__name__)


def build_article_url(base_url: str, lang: str, pid: str) -> str:
    """Build the public /{lang}/article/{pid} article page URL."""
    return f"{base_url.rstrip('/')}/{lang}/article/{pid}"


def load_square_logo(logo_path: Path) -> Image.Image:
    """Pad the logo onto a transparent square canvas so qrcode's forced
    square resize doesn't stretch/distort it."""
    logo = Image.open(logo_path).convert("RGBA")
    side = max(logo.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    offset = ((side - logo.width) // 2, (side - logo.height) // 2)
    canvas.paste(logo, offset, mask=logo)
    return canvas


def generate_qrcode(
    url: str,
    output_path: str,
    box_size: int = 10,
    border: int = 4,
    embedded_image_ratio: float = 0.35,
) -> None:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(
        image_factory=StyledPilImage,
        embedded_image=load_square_logo(LOGO_PATH),
        embedded_image_ratio=embedded_image_ratio,
    )
    img.save(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a QR code pointing to a Journal of Digital History article page."
    )
    parser.add_argument("pid", nargs="?", default=None, help="Article pid, e.g. 12345")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output image file path (default: qrcode-<pid>.png)",
    )
    parser.add_argument(
        "--base-url",
        default="https://journalofdigitalhistory.org",
        help="Base URL of the JDH front-end (default: production site)",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language path segment used by the front-end router (default: en)",
    )
    parser.add_argument(
        "--url",
        default=None,
        help="Skip URL building and encode this URL directly instead of the article page",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
        stream=sys.stderr,
    )

    pid = args.pid or get_pid_from_repo()

    output_path = args.output or f"qrcode-{pid}.png"
    url = args.url or build_article_url(args.base_url, args.lang, pid)

    try:
        logger.info("Encoding URL: %s", url)
        generate_qrcode(url, output_path)
        logger.info("✅ QR code written to %s", output_path)
    except Exception as e:
        logger.error("Error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()