# Tools — Rural Hide and Seek

Hide and Seek-specific scripts. The cross-game vehicle-stations generator lives in [`/stations-generator/`](../../stations-generator/).

---

## `ocr_expansion_cards.py`

OCRs the scanned Vol. 1 expansion-card PDF and splits the result into per-card sections. Reads from and writes to `.input/expansion-cards-ocr/`, which is gitignored — the output is for personal reference only and never committed (the official card text is copyrighted; see the repo's [`reference/README.md`](../reference/README.md) on the no-verbatim-source-text posture).

Run it directly:

```bash
uv run python hide-and-seek/tools/ocr_expansion_cards.py
```

<!-- TODO: Add map generation, investigation book helpers, or other Hide and Seek-specific utilities here. -->

---

## Requirements

Python dependencies for all tools in this project are managed by the root [`pyproject.toml`](../../pyproject.toml) using [uv](https://github.com/astral-sh/uv).

---

## License

Code in this directory is licensed under the [MIT License](../../LICENSE).
