# Structural Notes on the Original Hide + Seek

High-level structural notes only — **not** a reproduction of the rulebook. For verbatim rules, follow the links in [`sources.md`](./sources.md).

> Paraphrased structural reference for the original game. Numbers and category names below are factual; the framing is in our own words. Rural-variant rules and design decisions live in [`../rules.md`](../rules.md), not here — this file is purely about the official Hide + Seek.

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

The official rulebook publishes target transit-station counts per size (rough order: 30–100, 100–500, 500+). See your rulebook for the full table.

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

Repeat-asks cost more (the cost is multiplied each subsequent time the same question is asked). The Investigation Book is the canonical list — see your physical Investigation Book or the Fandom wiki under [`sources.md`](./sources.md) for the verbatim wording.

### Per-category structure

What can be plugged into each question's blanks.

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

---

## Hider deck composition

Three card types:

- **Time bonuses** — held until end of round, then added to the hider's time total. Five denominations in the base deck, with copy counts skewed toward smaller bonuses (25 / 15 / 10 / 3 / 2). Each card prints three values, one per game size — see [`cards.md`](./cards.md) for the table.
- **Power-ups** — utility cards. The base deck has seven types: Veto Question, Randomize Question, Duplicate Card, Move, two Discard-and-redraw variants, and a Hand-size expander.
- **Curses** — penalties imposed on the seekers, played at the hider's discretion. Each has a casting cost. The base deck ships 24 unique curses; see [`cards.md`](./cards.md) for the inventory and the taxonomy below for the mechanic clustering.

Hand limit is 6 cards by default; certain power-ups raise it. Drawing past the limit forces an immediate play-or-discard.

The Vol. 1 expansion adds 50 curses, 30 power-ups, and a set of 14 metric-unit replacements for the original distance cards. See the official expansion PDF in [`sources.md`](./sources.md) for full mechanics.

### Curse mechanic taxonomy

The 24 base-deck curses cluster into a handful of mechanical families. This grouping is analytical commentary — it's how mechanics behave, not what each card says. For verbatim card text, see your physical deck or the Fandom wiki entries (CC-BY-SA, importable into [`wiki/`](./wiki/)).

For the canonical name-only inventory of every card, see [`cards.md`](./cards.md). The taxonomy below covers the 24 base-deck curses plus 8 expansion curses whose mechanics we have via [`wiki/curses-uk-season-subset.md`](./wiki/curses-uk-season-subset.md); the † marker tags those 8.

| Family | What the family does | Curses in this family |
|--------|---------------------|------------------------|
| Movement restrictions | Constrain how the seekers can travel between locations | Right Turn · Gambler's Feet · U-Turn · Jammed Door · Express Route† · Rewind† |
| Detour gating | Force the seekers to a specific kind of location or activity before resuming play | Bridge Troll · Distant Cuisine · Mediocre Travel Agent · Queue† |
| Skill-challenge gating | Gate the next question behind a physical or puzzle task | Endless Tumble · Hidden Hangman · Cairn · Labyrinth · Bird Guide · Ransom Note |
| Acquisition / carrying handicaps | Make the seekers obtain and carry objects (with bonuses to the hider on loss) | Water Weight · Egg Partner · Lemon Phylactery · Impressionable Consumer |
| Photo conditions | Gate the next question behind a photo the seekers must produce or identify | Zoologist · Luxury Car · Unguided Tourist |
| Question, info, and communication restrictions | Reduce or constrain the seekers' question pool, ask conditions, or coordination | Drained Brain · Spotty Memory · Urban Explorer · Void† · Plagued Word† · Zipped Lip† |
| Hider economy / zone manipulation | Mechanical advantage for the hider — extra draws, bigger time bonuses, zone resizing | Overflowing Chalice · Prosperous Home† · Tiny Home† |

---

## The "Playing With Cars (Or On Foot)" experimental variant

The official rulebook's **Experimental Game Designs** section includes a "Playing With Cars (Or On Foot)" variant for areas without enough transit to support even the smallest game. Paraphrased — see your rulebook for the canonical text:

- **Map setup**: drop the transit overlay; just draw the map borders. Without stations as anchors, defining what counts as a valid hiding spot needs more care.
- **Hiding zones**: still a circle of size-dependent radius, but its center moves from a transit station to a *street terminus* — a point where a named street ends, either at an intersection with another named street or at a dead end. The terminus inherits the station's role: photo questions that referenced the station are taken there; questions that referenced the station's name now reference the street's name.
- **Questions**: most carry over unchanged. Drop questions that reference transit frequency. Questions that refer to the hider's station now refer to the street terminus.
- **Curses**: any curse that's blocked while seekers are on transit is also blocked while seekers are in a moving car. Curses that target "transportation" or "transit" treat cars as transit.

The rural variant in this repo deliberately does not inherit this experimental design — see [`../rules.md`](../rules.md) "Approach" for the alternative path it takes. This section is documented here as part of the official-game structural reference.
