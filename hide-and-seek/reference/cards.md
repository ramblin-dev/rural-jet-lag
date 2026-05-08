# Cards Reference

A name-only inventory of every card in the original Hide + Seek base deck and Vol. 1 expansion. Names are factual inventory, not protectable expression — see [`README.md`](./README.md) for the licensing posture. For mechanic descriptions, see [`notes.md`](./notes.md) (paraphrased structural taxonomy) or [`wiki/`](./wiki/) (CC-BY-SA wiki imports). For verbatim card text, see the sources in [`sources.md`](./sources.md).

## Adaptation markers

Each card carries an adaptation marker indicating how it lands in the rural variant. The markers are *predicted* friction points inferred from reading the card mechanics, **not** measured outcomes — we have no rural play data. Treat them as a starting point for design review, not as a settled assessment.

- *(blank)* — appears geography-agnostic or vehicle-compatible based on its mechanic
- **⚠** — likely needs adaptation (distance rescaling, density-assumption rework, or urban-subject substitution)
- **✗** — likely needs replacement (the mechanic explicitly references transit, walking-only motion, or another concept that doesn't apply in vehicle play)
- **?** — uncertain; flagged for design review

Quantities and names come from your physical deck inventory.

---

## Base game

### Time bonuses

Each time-bonus card prints three values, one per game size. The card's value at a given game is the column matching that game's size tier. Quantities are per card (across all three values).

| S | M | L | Quantity |
|--:|--:|--:|---------:|
|  2 |  3 |  5 | 25 |
|  4 |  6 | 10 | 15 |
|  6 |  9 | 15 | 10 |
|  8 | 12 | 20 |  3 |
| 12 | 18 | 30 |  2 |

Values are in minutes. No marker — values already scale with the original game's chosen size tier, so the rural variant addresses the rescale concern by picking a size, not by retuning bonuses.

### Power-ups

| Card | Quantity | Marker |
|------|---------:|--------|
| Veto Question | 4 |   |
| Randomize Question | 4 |   |
| Discard 1, Draw 2 | 4 |   |
| Discard 2, Draw 3 | 4 |   |
| Duplicate Card | 2 |   |
| Draw 1, Expand 1 | 2 |   |
| Move | 1 |   |

All power-ups are geography-agnostic and appear to survive unchanged.

### Curses

24 unique curses in the base deck (one copy each).

| Curse | Marker | Mechanic family (per `notes.md`) |
|-------|--------|----------------------------------|
| Curse of the Bird Guide |   | Skill-challenge gating |
| Curse of the Bridge Troll | ⚠ | Detour gating |
| Curse of the Cairn |   | Skill-challenge gating |
| Curse of the Distant Cuisine | ⚠ | Detour gating |
| Curse of the Drained Brain |   | Question/info/communication restrictions |
| Curse of the Egg Partner |   | Acquisition / carrying |
| Curse of the Endless Tumble |   | Skill-challenge gating |
| Curse of the Gambler's Feet | ✗ | Movement restrictions |
| Curse of the Hidden Hangman |   | Skill-challenge gating |
| Curse of the Impressionable Consumer | ⚠ | Acquisition / carrying |
| Curse of the Jammed Door | ⚠ | Movement restrictions |
| Curse of the Labyrinth |   | Skill-challenge gating |
| Curse of the Lemon Phylactery |   | Acquisition / carrying |
| Curse of the Luxury Car | ⚠ | Photo conditions |
| Curse of the Mediocre Travel Agent | ⚠ | Detour gating |
| Curse of the Overflowing Chalice |   | Hider economy / zone manipulation |
| Curse of the Ransom Note |   | Skill-challenge gating |
| Curse of the Right Turn |   | Movement restrictions |
| Curse of the Spotty Memory |   | Question/info/communication restrictions |
| Curse of the Unguided Tourist | ⚠ | Photo conditions |
| Curse of the Urban Explorer | ✗ | Question/info/communication restrictions |
| Curse of the U-Turn | ✗ | Movement restrictions |
| Curse of the Water Weight | ⚠ | Acquisition / carrying |
| Curse of the Zoologist |   | Photo conditions |

### Blank cards

| Card | Quantity | Marker |
|------|---------:|--------|
| Blank | 25 |   |

Confirmed against your physical deck. Customization vector — rural-specific curses can be authored on these without modifying the printed deck. Likely the right place to introduce vehicle/range mechanics.

---

## Expansion Pack Vol. 1

Your box says **50 curses, 30 power-ups, 14 metric cards**. With your deck inventory in hand:

- **50 curses** ✓ exact match.
- **30 power-ups** reconciles by counting time bonuses as a power-up subtype: 12 time-bonus power-ups + 18 other power-ups = 30. We list them in separate subsections below for clarity.
- **14 metric cards** are 14 separate physical cards, each a metric-distance variant of one of the 50 imperial curses — same title, same mechanic, distances in km/m instead of miles/feet. The box wording "same as base game in metric units" is inaccurate copy. **Total physical expansion curse cards: 64** (50 imperial + 14 metric variants).

### Power-ups (30 cards across 8 types)

The expansion box counts time bonuses as power-ups; we follow that convention here while keeping the time-bonus subset listed separately so the mechanics stay legible.

#### Time bonus power-ups (12 cards across 3 types)

Like the base deck, fixed-minute cards print three values, one per game size. Percentage time bonuses award a percent of the hider's total hiding time at end of round and don't stack with other bonuses (per the official expansion PDF).

| S | M | L | Quantity |
|--:|--:|--:|---------:|
| 20 | 36 | 60 | 4 |
| 5% | 5% | 5% | 4 |
| 10% | 10% | 10% | 4 |

#### Other power-ups (18 cards across 5 types)

| Card | Quantity | Marker |
|------|---------:|--------|
| Discard 3, Draw 4 | 4 |   |
| Draw 2, Expand 2 | 2 |   |
| Discard Me | 2 |   |
| Nothing | 5 |   |
| Time Trap | 5 | ✗ |

**Time Trap** is transit-coupled per the expansion PDF — placed on transit stations, awards extra time to the hider when seekers pass through.

### Curses

50 distinct expansion curses by name. The Metric column marks the 14 curses that have a separate metric-unit physical card alongside the imperial version (same title, same mechanic, distances in km/m). Total physical curse cards in the expansion: 64.

Markers reflect mechanic data from the official expansion PDF and from `wiki/curses-uk-season-subset.md` for the eight curses present there. Curses with no published mechanic detail are listed without a marker or family — those are gaps to fill from the physical cards.

| Curse | Metric | Marker | Likely family |
|-------|:------:|:------:|---------------|
| Curse of the 5-Minute King |   |   |   |
| Curse of the Anonymous Benefactor |   |   |   |
| Curse of the Archaeologist |   |   | Skill-challenge gating |
| Curse of the Bargain Hunter |   | ⚠ | Detour gating / Acquisition |
| Curse of the Blind Wanderer | ✓ |   |   |
| Curse of the Chasm |   |   |   |
| Curse of the Clone |   |   | Acquisition / clothing |
| Curse of the Curious Explorer | ✓ | ⚠ | Detour gating |
| Curse of the Data Leak |   | ✗ | Movement restrictions |
| Curse of the Divine Blessing |   |   |   |
| Curse of the Empty Mind |   |   | Question/info restrictions |
| Curse of the Express Route |   | ✗ | Movement restrictions |
| Curse of Featherless Flight |   |   | Skill-challenge gating |
| Curse of the Freewheeler | ✓ |   |   |
| Curse of the Gilded Inquiry |   |   | Question/info restrictions |
| Curse of the Grass-Toucher | ✓ |   |   |
| Curse of the Hide-and-Seek-Ception | ✓ |   | Communication (multi-seeker only) |
| Curse of the Impenetrable Fog |   |   | Movement restrictions |
| Curse of the Landline | ✓ |   |   |
| Curse of the Long Shot | ✓ | ✗ | Movement restrictions (transit freeze) |
| Curse of the Mind Meld |   |   |   |
| Curse of the Non-Dominant Hand |   |   |   |
| Curse of the Okaihau Express |   |   | Skill-challenge gating |
| Curse of the Open Mind |   |   |   |
| Curse of the Oracle |   |   |   |
| Curse of the Passenger Princess |   |   | Communication (multi-seeker only) |
| Curse of the Plagued Word | ✓ | ⚠ | Question/info restrictions |
| Curse of the Planespotter | ✓ |   |   |
| Curse of the Pomologist |   |   | Skill-challenge gating |
| Curse of the Pong Champion | ✓ |   | Skill-challenge gating |
| Curse of the Post Office | ✓ | ⚠ | Detour gating |
| Curse of the Prophet |   |   |   |
| Curse of the Prosperous Home |   |   | Hider economy / zone manipulation |
| Curse of the Queue |   |   | Detour gating |
| Curse of the Quill | ✓ |   | Skill-challenge gating |
| Curse of the Rewind |   |   | Movement restrictions |
| Curse of the Runner |   |   | Movement restrictions |
| Curse of the Seabird | ✓ | ⚠ | Photo conditions |
| Curse of the Seventh Seal |   |   |   |
| Curse of the Shark |   |   | Question/info restrictions (?) |
| Curse of the Shrewd Critic | ✓ | ⚠ | Question/info restrictions |
| Curse of the Sniper |   |   | Photo conditions |
| Curse of the Soothsayer |   |   | Hider economy / zone manipulation |
| Curse of the Strider |   |   |   |
| Curse of the Strongman |   |   |   |
| Curse of the Tiny Home |   |   | Hider economy / zone manipulation |
| Curse of the Trickster |   |   | Question/info restrictions |
| Curse of the Untethered Spirit |   |   |   |
| Curse of the Void |   |   | Question/info restrictions |
| Curse of the Zipped Lip |   |   | Question/info/communication restrictions |


---

## Remaining gaps

Inventory is now complete by name. The remaining gap is **mechanic detail for the 18 expansion curses without markers / family**:

5-Minute King, Anonymous Benefactor, Blind Wanderer, Chasm, Divine Blessing, Freewheeler, Grass-Toucher, Landline, Mind Meld, Non-Dominant Hand, Open Mind, Oracle, Planespotter, Prophet, Seventh Seal, Strider, Strongman, Untethered Spirit.

Their mechanics are visible only on the physical cards; the official expansion PDF doesn't clarify them and they aren't on any wiki page we've imported. Filling those in unlocks marker assignment and family slotting. A one-line family classification per curse is enough — no verbatim card text needs to enter the repo.
