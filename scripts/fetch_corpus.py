"""Download the FastAPI documentation pages used as the evaluation corpus.

The corpus is fetched from a pinned commit so results are reproducible.
FastAPI is MIT licensed; its LICENSE file is saved alongside the pages.
"""
import io
import pathlib
import sys
import tarfile
import urllib.request

COMMIT = "79cab5bed28b24d92c185d236feb33f5783dfeb3"  # pinned for reproducible evaluation
ARCHIVE_URL = f"https://codeload.github.com/tiangolo/fastapi/tar.gz/{COMMIT}"
OUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "data" / "fastapi_docs"

PAGES = [
    "background-tasks", "body", "body-multiple-params", "body-nested-models",
    "body-updates", "cookie-params", "cors", "debugging", "extra-data-types",
    "handling-errors", "header-params", "metadata", "middleware", "path-operation-configuration",
    "path-params", "path-params-numeric-validations", "query-param-models", "query-params",
    "query-params-str-validations", "request-files", "request-forms-and-files", "response-model",
    "response-status-code", "server-sent-events", "static-files", "stream-json-lines", "testing",
    "body-fields", "request-form-models",
]


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {ARCHIVE_URL}")
    with urllib.request.urlopen(ARCHIVE_URL, timeout=60) as response:
        archive = tarfile.open(fileobj=io.BytesIO(response.read()), mode="r:gz")

    # GitHub names the top-level folder "<repo>-<ref>", so detect it instead of hardcoding it.
    prefix = archive.getmembers()[0].name.split("/")[0]
    tutorial_dir = f"{prefix}/docs/en/docs/tutorial/"

    saved = 0
    for name in PAGES:
        try:
            member = archive.extractfile(f"{tutorial_dir}{name}.md")
        except KeyError:
            print(f"warning: {name}.md not found in archive", file=sys.stderr)
            continue
        (OUT_DIR / f"{name}.md").write_bytes(member.read())
        saved += 1

    try:
        license_file = archive.extractfile(f"{prefix}/LICENSE")
    except KeyError:
        license_file = None
    if license_file is not None:
        (OUT_DIR / "LICENSE_FASTAPI").write_bytes(license_file.read())

    print(f"Saved {saved} pages to {OUT_DIR}")
    return 0 if saved >= 25 else 1


if __name__ == "__main__":
    sys.exit(main())
