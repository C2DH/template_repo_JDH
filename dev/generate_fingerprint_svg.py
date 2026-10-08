#!/usr/bin/env python3

"""
generate_fingerprint_svg.py

Generate an ArticleFingerprint SVG for a JDH article, given its pid,
by resolving the article's notebook_url via the JDH API and then
rendering the site's /fingerprint-viewer page in a headless browser
to extract the live SVG output.

Requirements:
    pip install playwright requests
    playwright install chromium

Usage:
    python generate_fingerprint_svg.py 12345
    python generate_fingerprint_svg.py 12345 -o fingerprint.svg
    python generate_fingerprint_svg.py 12345 --base-url https://journalofdigitalhistory.org --lang en
"""

import argparse
import base64
import sys
import urllib.parse

import requests
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .get_pid import get_pid_from_repo

# Path prefix used by the JDH nginx/django proxy to serve raw GitHub content.
# See jdh/settings.py JDHSEO_PROXY_PATH_GITHUB and jdhapi/signals.py.
PROXY_PATH_GITHUB = "/proxy-githubusercontent"
RAW_GITHUB_HOST = "https://raw.githubusercontent.com"


def get_notebook_url(api_base_url: str, pid: str) -> str:
    """Resolve an article pid to its (encoded) notebook_url via the JDH API."""
    endpoint = f"{api_base_url.rstrip('/')}/api/articles/{pid}"
    resp = requests.get(endpoint, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    notebook_url = data.get("notebook_url")
    if not notebook_url:
        raise ValueError(
            f"No 'notebook_url' found for article pid={pid} at {endpoint}. "
            f"Response keys: {list(data.keys())}"
        )
    return notebook_url


def decode_notebook_url(encoded_notebook_url: str) -> str:
    """Decode the API's `notebook_url` field into an absolute, directly
    fetchable raw GitHub URL.

    `Article.notebook_url` is NOT a plain URL: it is
    base64(percent-encoded relative proxy path), produced in
    jdhapi/signals.py as something like:

        /proxy-githubusercontent/jdh-observer/<repo>/main/<notebook_path>

    That relative path is only resolvable through the JDH nginx proxy
    (JDHSEO_PROXY_HOST + JDHSEO_PROXY_PATH_GITHUB). Since the front-end
    /fingerprint-viewer page fetches the notebook JSON directly from the
    browser, we need to turn it into a real, CORS-accessible absolute URL
    on raw.githubusercontent.com instead.
    """
    try:
        decoded_bytes = base64.b64decode(encoded_notebook_url)
        decoded_path = urllib.parse.unquote(decoded_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(
            f"Could not base64-decode notebook_url {encoded_notebook_url!r}: {e}"
        )

    if decoded_path.startswith(("http://", "https://")):
        # Already an absolute URL once decoded.
        return decoded_path

    if decoded_path.startswith(PROXY_PATH_GITHUB):
        remainder = decoded_path[len(PROXY_PATH_GITHUB):]
        return f"{RAW_GITHUB_HOST}{remainder}"

    raise ValueError(
        f"Unrecognized notebook_url format after decoding: {decoded_path!r} "
        f"(expected it to start with {PROXY_PATH_GITHUB!r} or http(s)://)"
    )


def build_fingerprint_viewer_url(base_url: str, lang: str, notebook_url: str) -> str:
    """Build the /{lang}/fingerprint-viewer?url=<notebook_url> URL."""
    query = urllib.parse.urlencode({"url": notebook_url})
    return f"{base_url.rstrip('/')}/{lang}/fingerprint-viewer?{query}"


def render_fingerprint_svg(
    page_url: str,
    timeout_ms: int = 60000,
    headless: bool = True,
) -> str:
    """Load the fingerprint-viewer page in a headless browser and return the SVG markup."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        try:
            page = browser.new_page()
            page.goto(page_url, wait_until="networkidle", timeout=timeout_ms)

            # Wait until the ArticleFingerprint svg has actual content (cells rendered),
            # i.e. parsing/fetching of the notebook has completed.
            try:
                page.wait_for_selector(
                    "svg.ArticleFingerprint g g",
                    timeout=timeout_ms,
                )
            except PlaywrightTimeoutError:
                raise RuntimeError(
                    "Timed out waiting for the fingerprint SVG to render. "
                    "The notebook URL may be invalid, unreachable, or malformed."
                )

            svg_html = page.eval_on_selector(
                "svg.ArticleFingerprint",
                "el => el.outerHTML",
            )
            if not svg_html:
                raise RuntimeError("Could not find rendered SVG element on the page.")
            return svg_html
        finally:
            browser.close()


def wrap_svg_standalone(svg_fragment: str) -> str:
    """Ensure the SVG has an xml declaration for standalone use."""
    if svg_fragment.lstrip().startswith("<?xml"):
        return svg_fragment
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_fragment


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Journal of Digital History article fingerprint as an SVG file."
    )
    parser.add_argument("pid", nargs="?", default=None, help="Article pid, e.g. 12345")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output SVG file path (default: fingerprint-<pid>.svg)",
    )
    parser.add_argument(
        "--base-url",
        default="https://journalofdigitalhistory.org",
        help="Base URL of the JDH front-end (default: production site)",
    )
    parser.add_argument(
        "--api-base-url",
        default=None,
        help="Base URL of the JDH API, if different from --base-url",
    )
    parser.add_argument(
        "--lang",
        default="en",
        help="Language path segment used by the front-end router (default: en)",
    )
    parser.add_argument(
        "--notebook-url",
        default=None,
        help="Skip the API lookup and use this notebook URL directly",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60000,
        help="Timeout in ms for page load / render (default: 60000)",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Run the browser in headed (visible) mode for debugging",
    )
    args = parser.parse_args()
    pid = args.pid or get_pid_from_repo()

    api_base_url = args.api_base_url or args.base_url
    output_path = args.output or f"fingerprint-{pid}.svg"

    try:
        if args.notebook_url:
            notebook_url = args.notebook_url
        else:
            print(f"Resolving notebook_url for pid={pid} ...", file=sys.stderr)
            encoded_notebook_url = get_notebook_url(api_base_url, pid)
            print(f"Encoded notebook_url: {encoded_notebook_url}", file=sys.stderr)
            notebook_url = decode_notebook_url(encoded_notebook_url)
        print(f"Notebook URL: {notebook_url}", file=sys.stderr)

        page_url = build_fingerprint_viewer_url(args.base_url, args.lang, notebook_url)
        print(f"Rendering: {page_url}", file=sys.stderr)

        svg_markup = render_fingerprint_svg(
            page_url,
            timeout_ms=args.timeout,
            headless=not args.show_browser,
        )
        svg_markup = wrap_svg_standalone(svg_markup)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(svg_markup)

        print(f"✅ SVG written to {output_path}")

    except requests.HTTPError as e:
        print(f"API request failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
