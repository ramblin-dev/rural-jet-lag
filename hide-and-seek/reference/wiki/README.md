# Fandom Wiki Imports

Content in this subtree is **derived from the Jet Lag Fandom wiki** (<https://jetlag.fandom.com/>) and is licensed under **CC BY-SA 4.0**, *not* the repo-default CC BY 4.0.

> This is an unofficial fan project. Not affiliated with Jet Lag: The Game, Nebula, or Wendover Productions.

---

## Why a separate license

Fandom wiki content is published under CC BY-SA 4.0. To reuse it we must:

1. **Attribute** the source page (URL + "Jet Lag: The Wiki contributors").
2. **Share alike** — any derivative of this content is also CC BY-SA 4.0, not CC BY.

Keeping wiki-sourced content isolated to this directory preserves both licenses cleanly: everything outside `wiki/` stays CC BY 4.0; everything inside is CC BY-SA 4.0. Don't merge wiki content with original notes in the same file — the SA boundary needs to be obvious to a downstream reuser.

Full license text: <https://creativecommons.org/licenses/by-sa/4.0/legalcode>

---

## Import format

Save each imported page as `<slug>.md` with this frontmatter:

```yaml
---
source: https://jetlag.fandom.com/wiki/<page>
retrieved: YYYY-MM-DD
license: CC BY-SA 4.0
attribution: Jet Lag: The Wiki contributors
---
```

Followed by the imported content.

---

## Currently imported

- [`curses-uk-season-subset.md`](./curses-uk-season-subset.md) — 8 curses from the [Hide + Seek: UK / Curses](https://jetlag.fandom.com/wiki/Hide_%2B_Seek:_UK/Curses) page (retrieved 2026-05-06). Selective subset chosen to fill the gap between the lifack base deck and the AJV6812 Sydney variant deck.
