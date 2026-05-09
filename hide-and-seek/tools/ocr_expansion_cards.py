"""OCR each page of the scanned expansion-card PDF, then split by card headers.

Reads .input/expansion-cards-ocr/pages/page-{1..6}.png (rendered from the
scanned PDF), runs OCR on each whole page, and writes:
  - .input/expansion-cards-ocr/pages/page-{N}.txt  (raw per-page OCR)
  - .input/expansion-cards-ocr/cards.md            (split by card title)

Output is meant for personal reference only — `.input/` is gitignored.
"""

from __future__ import annotations

import re
from pathlib import Path

from rapidocr_onnxruntime import RapidOCR

ROOT = Path(__file__).resolve().parents[2]
PAGES_DIR = ROOT / ".input/expansion-cards-ocr/pages"
OUT_MD = ROOT / ".input/expansion-cards-ocr/cards.md"

# Match card titles. Curses say "CURSE OF [THE] X"; power-ups have varied
# titles, so we treat anything matching the all-caps headline pattern at the
# start of a card block as a header. Detection is heuristic — review the
# resulting cards.md by hand.
CURSE_RE = re.compile(r"^\s*CURSE\s*OF\b", re.IGNORECASE)


def ocr_page(ocr: RapidOCR, page_path: Path) -> str:
    result, _ = ocr(str(page_path))
    if not result:
        return ""
    return "\n".join(line[1] for line in result)


def main() -> None:
    ocr = RapidOCR()
    page_texts: list[tuple[int, str]] = []
    for page_path in sorted(PAGES_DIR.glob("page-*.png")):
        page_num = int(page_path.stem.split("-")[1])
        text = ocr_page(ocr, page_path)
        (page_path.with_suffix(".txt")).write_text(text)
        page_texts.append((page_num, text))
        print(f"page-{page_num}: {len(text)} chars, "
              f"{sum(1 for line in text.splitlines() if CURSE_RE.match(line))} curse headers")

    OUT_MD.write_text(
        "# Expansion cards — raw OCR\n\n"
        "Per-page OCR dumps from the scanned expansion-card PDF. Card boundaries\n"
        "in the OCR stream are noisy — review and split by hand into the curse / "
        "power-up entries we still need full text for. `.input/` is gitignored; "
        "this file is for personal reference only.\n\n"
        + "\n\n".join(
            f"---\n\n## Page {n}\n\n```\n{t}\n```" for n, t in page_texts
        )
    )
    print(f"\nWrote {OUT_MD}")


if __name__ == "__main__":
    main()
