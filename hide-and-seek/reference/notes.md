# Structural Notes on the Original Hide + Seek

High-level structural notes only — **not** a reproduction of the rulebook. For verbatim rules, follow the links in [`sources.md`](./sources.md).

> This file describes the *shape* of the original game so the rural adaptation in [`../rules/`](../rules/) can build on it deliberately. It's paraphrased structural reference, not source text. Numbers and category names below are factual; the framing is in our own words.

---

## Five-step gameplay loop

1. The hider uses public transit to reach a hiding spot inside a chosen hiding zone.
2. The seekers ask questions from six categories to narrow down where the hider is.
3. Each answered question lets the hider draw cards from the hider deck.
4. When found, the next player becomes the hider.
5. Whoever achieves the longest *single* hiding run wins (hiding time is not cumulative across rounds).

---

## Game sizes

The official game ships three size tiers. Map and duration scale together:

| Size | Geographic span | Duration | Hiding period | Hiding-zone radius |
|------|-----------------|----------|--------------|---------------------|
| Small | A town, a small city, or part of a large city | 4–8 hours | 30 min | ¼ mile |
| Medium | A major city, metro area, or region | ~1 day | 60 min | ¼ mile |
| Large | A large region or whole country | 2–4 days | 180 min | ½ mile |

Lifack publishes target transit-station counts per size (rough order: 30–100, 100–500, 500+) — useful as a complexity calibration even when transit isn't the underlying network. See [Choosing a Transit System on lifack.ch](https://www.lifack.ch/docs/setting_up_your_map/choosing_a_transit_system/) for the full table.

<!-- TODO: pick analogous calibration targets for rural play (e.g. number of valid hide anchors per square mile) -->

---

## Round structure

- **Round start:** all players gather at a starting location inside the map. Hider takes the hider deck; seekers take the investigation book. Both sides keep dice and a rulebook reference. Seekers turn on a location tracker (phone live-share suffices).
- **Hiding period:** hider-only movement on transit + foot to reach their hiding zone, then must remain inside the zone for the rest of the round.
- **Seeking phase:** seekers ask questions, get card draws, and try to enter the hiding zone.
- **End game trigger:** seekers cross into the hiding zone *while no longer on transit*. At this point the hider must remain at a single publicly-accessible hiding spot. "I cannot answer the question" becomes a valid response when movement restrictions make it impossible.
- **Found:** seekers within 5 feet of the hider AND visually identified. Time bonuses still in the hider's hand are added at this point.
- **Rotation:** 10-minute prep window for the next hider; deck is reshuffled and handed off; the next round starts from the previous hider's spot.

---

## Question categories

The Investigation Book groups questions into six categories. Each has its own draw-and-keep reward and answer window:

| Category | Shape | Draw / keep | Answer window |
|----------|-------|-------------|---------------|
| Matching | Compare hider's nearest X to seeker's nearest X | 3 / 1 | 5 min |
| Measuring | Compare hider's distance-to-X with seeker's | 3 / 1 | 5 min |
| Radar | Hider within distance D of seeker? | 2 / 1 | 5 min |
| Thermometer | Did seeker get closer after moving D? | 2 / 1 | 5 min |
| Tentacles | Among Xs within D of hider, which is nearest? | 4 / 2 | 5 min |
| Photos | Hider sends a photo of [subject] | 1 (no pick) | 10 min S/M, 20 min L |

Repeat-asks cost more (the cost is multiplied each subsequent time the same question is asked). The Investigation Book is the canonical list — see lifack and the Fandom wiki under [`sources.md`](./sources.md) for the verbatim wording.

### Per-category structure

What can be plugged into each question's blanks. Subject pools and distance buckets are what the rural adaptation will most need to re-ground.

**Matching** and **Measuring** share most of their subject pools, organized into rough buckets:

- *Transit-anchored* — commercial airport, transit line / high-speed train line, rail station, station-name length, street-or-path
- *Administrative divisions* — 1st, 2nd, 3rd, 4th admin divisions (and their borders for Measuring)
- *Natural* — mountain, landmass, body of water, coastline, sea level, park
- *Places of interest* — amusement park, zoo, aquarium, golf course, museum, movie theater
- *Public utilities* — hospital, library, foreign consulate

**Radar** distances (all sizes): ¼, ½, 1, 3, 5, 10, 25, 50, 100 miles, plus a "choose" wildcard.

**Thermometer** distances tier by game size: ½ and 3 miles always available; 10 miles unlocks at Medium; 50 miles unlocks at Large.

**Tentacles** subject + distance tiers:
- Medium and Large (1 mile radius): museums, libraries, movie theaters, hospitals
- Large only (15 mile radius): metro lines, zoos, aquariums, amusement parks

**Photos** subjects tier by game size:
- *All sizes:* a tree, the sky, you, widest street, tallest structure in sightline, any building visible from station
- *Add at Medium and Large:* tallest building visible from station, trace nearest street/path, two buildings, restaurant interior, train platform, park, grocery store aisle, place of worship
- *Add at Large:* ½ mile of streets traced, tallest mountain visible from station, biggest body of water in zone, five buildings

<!-- TODO: per-category translation decisions for the rural variant
     - Matching/Measuring: which transit-anchored subjects translate (rail station → ?), which natural/POI subjects survive, which administrative-division references rescale meaningfully at county scale
     - Radar: rescale buckets — rural play likely needs ranges starting much larger (1 mile floor or higher) and extending further (200+ miles)
     - Thermometer: same rescale concern; the ½-mile-everywhere baseline is walking-scale
     - Tentacles: rural-density subjects (gas stations? grain elevators? county seats?) at appropriate radii
     - Photos: the urban-centric subjects (train platform, restaurant interior, grocery store aisle) need rural substitutes; "any building visible from station" needs an anchor replacement
-->


---

## Hider deck composition

Three card types:

- **Time bonuses** — held until end of round, then added to the hider's time total. Five denominations in the base deck (3, 6, 9, 12, 18 minutes), with copy counts skewed toward smaller bonuses (lifack and Sydney digitizations both show 25 / 15 / 10 / 3 / 2).
- **Power-ups** — utility cards. Lifack's printing has seven types: Veto, Randomize, Duplicate, Move, two Discard-and-redraw variants, and a Hand-size expander. (The AJV6812 Sydney variant doesn't list a Move power-up, so the deck appears to vary by printing — see [`sources.md`](./sources.md).)
- **Curses** — penalties imposed on the seekers, played at the hider's discretion. Each has a casting cost. Lifack ships 24 unique curses; the Sydney variant lists 28. The two decks share most names but diverge on a handful (see taxonomy below).

Hand limit is 6 cards by default; certain power-ups raise it. Drawing past the limit forces an immediate play-or-discard.

The Vol. 1 expansion adds 50 curses, 30 power-ups, and a set of 14 metric-unit replacements for the original distance cards. See the official expansion PDF in [`sources.md`](./sources.md) for full mechanics.

### Curse mechanic taxonomy

The 24 base-deck curses (per lifack) cluster into a handful of mechanical families. This grouping is analytical commentary — it's how mechanics behave, not what each card says. For verbatim card text, see the lifack pages (community recreation, © Collin Jones) or the Fandom wiki entries (CC-BY-SA, importable into [`wiki/`](./wiki/)).

Curses marked † come from the UK-season Fandom-wiki subset imported into [`wiki/curses-uk-season-subset.md`](./wiki/curses-uk-season-subset.md), not the lifack base deck. They appear in the AJV6812 Sydney variant card list and are included here for completeness when designing rural curses.

| Family | What the family does | Curses in this family |
|--------|---------------------|------------------------|
| Movement restrictions | Constrain how the seekers can travel between locations | Right Turn · Gambler's Feet · U-Turn · Jammed Door · Express Route† · Rewind† |
| Detour gating | Force the seekers to a specific kind of location or activity before resuming play | Bridge Troll · Distant Cuisine · Mediocre Travel Agent · Queue† |
| Skill-challenge gating | Gate the next question behind a physical or puzzle task | Endless Tumble · Hidden Hangman · Cairn · Labyrinth · Bird Guide · Ransom Note |
| Acquisition / carrying handicaps | Make the seekers obtain and carry objects (with bonuses to the hider on loss) | Water Weight · Egg Partner · Lemon Phylactery · Impressionable Consumer |
| Photo conditions | Gate the next question behind a photo the seekers must produce or identify | Zoologist · Luxury Car · Unguided Tourist |
| Question, info, and communication restrictions | Reduce or constrain the seekers' question pool, ask conditions, or coordination | Drained Brain · Spotty Memory · Urban Explorer · Void† · Plagued Word† · Zipped Lip† |
| Hider economy / zone manipulation | Mechanical advantage for the hider — extra draws, bigger time bonuses, zone resizing | Overflowing Chalice · Prosperous Home† · Tiny Home† |

#### Family-by-family relevance to the rural adaptation

- **Movement restrictions** — mostly need rewriting. Right Turn translates cleanly to driving; Gambler's Feet (per-step dice), U-Turn and Express Route (both transit-anchored) don't; Rewind (location-anchored) survives unchanged; Jammed Door (per-doorway dice) survives but its role shrinks when most movement is between buildings via vehicle.
- **Detour gating** — survives, but distances need rescaling. "Within X miles" tuned for transit-walkable scale is too small for county play. Queue (any line, anywhere) is fully transferable.
- **Skill-challenge gating** — most transferable family. These are standalone physical/puzzle tasks decoupled from transit. Likely the safest set to keep.
- **Acquisition / carrying handicaps** — survives in spirit, but the design tension flips: vehicles make carrying trivial. Either lean into vehicle-carry mechanics (e.g. items that must be visible on a person, not in a trunk) or rebalance toward objects that constrain regardless of vehicle.
- **Photo conditions** — survives. Subjects may need rural-friendly substitutes (e.g. a "more expensive car" is harder to find in low-traffic regions; a wild-animal match is easier).
- **Question, info, and communication restrictions** — Urban Explorer (transit-coupled) needs a vehicle-equivalent ("can't ask while driving" is the obvious port). The other six (Drained Brain, Spotty Memory, Void, Plagued Word, Zipped Lip — communication-only) are geography-agnostic and survive as-is. Plagued Word's 5-mile no-ask radius will probably want rescaling alongside the other distance buckets.
- **Hider economy / zone manipulation** — fully transferable; no geography assumptions. Note that Prosperous Home and Tiny Home both manipulate the hiding-zone radius, which makes them sensitive to whatever "zone" means in the rural variant (a circle around a vehicle-anchored point, vs. a property line, vs. a road segment, etc.).

<!-- TODO: when designing rural curses, decide whether to (a) port lifack's families one-for-one with rescaled distances, (b) add a vehicle-specific family (range-related curses, fuel-stop forced detours, breakdown-style penalties), or (c) drop some families and lean into others -->

---

## Playing without public transit

> This section is the hinge for the rural adaptation. **Read it before designing rural rules.**

Lifack's rulebook acknowledges that many areas don't have enough public transit to support even the smallest official game, and sketches a "cars or on foot" variant. The variant's design moves are worth knowing — both as a starting point and as a contrast point — for what this repo is building.

The lifack approach (paraphrased — see [Playing With Cars (Or On Foot)](https://www.lifack.ch/docs/experimental_game_designs/playing_with_cars_or_on_foot/) for the source):

- **Map setup**: drop the transit overlay; just draw the map borders. Without stations as anchors, defining what counts as a valid hiding spot needs more care.
- **Hiding zones**: still a circle of size-dependent radius, but its center moves from a transit station to a *street terminus* — a point where a named street ends, either at an intersection with another named street or at a dead end. The terminus inherits the station's role: photo questions that referenced the station are taken there; questions that referenced the station's name now reference the street's name.
- **Questions**: most carry over unchanged. Drop questions that reference transit frequency. Questions that refer to the hider's station now refer to the street terminus.
- **Curses**: any curse that's blocked while seekers are on transit is also blocked while seekers are in a moving car. Curses that target "transportation" or "transit" treat cars as transit.

### How the rural variant in this repo will differ

Lifack's variant is a *light* swap: replace one network (transit) with another point-anchor (street termini), keep mechanics roughly intact. That works in suburban or low-density urban settings.

The rural variant this repo targets is more aggressive — vehicle range becomes a primary game resource, geography is county-scale, and walkable-distance assumptions in the original mechanics need to be re-grounded against driving distances. So lifack's variant is a useful first checkpoint (it confirms the official ruleset can survive losing transit), but the rural-variant decisions in [`../rules/`](../rules/) will need to go further.

<!-- TODO: per-mechanic decisions that diverge from lifack's approach — what "anchor" replaces a transit station in rural play (county-seat? grain elevator? named road junction?), how vehicle range maps onto hiding-period budgets, etc. -->

---

## Adaptation pointers

Cross-reference each original mechanic to its rural counterpart in [`../rules/`](../rules/) as decisions are made. Likely decision points:

- Anchor for hiding zones (transit station → ?). Lifack's choice of street terminus is a benchmark; rural may want something else (junction of named county roads, named landmark, etc.).
- Walkable-distance assumptions in question costs (radius questions, photo subjects in walking range) → rescaled for driving distance.
- Photo subjects that assume urban subjects (grocery aisle, station entrance, restaurant interior) → rural-friendly substitutes or removed.
- End-game "no more transit" trigger → vehicle / range equivalent.
- Distance buckets (radar, thermometer) → rescaled for county-level play.
- Curses that reference transit → rewritten to reference vehicles / range, per the lifack convention.
