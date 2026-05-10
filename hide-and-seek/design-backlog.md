# Design Backlog — Hide and Seek

Ideas we've raised but aren't building yet. When one moves into active work, promote it out of this file into the relevant location (`rules.md`, `assets/`, etc.) and delete the entry here.

---

## Deck builds

A `decks/` (or `deck-builds/`) folder alongside `rules.md`, holding one markdown file per recommended deck configuration. Each file would name the build, describe the kind of rural area it suits (e.g. dense farmland counties, low-density mountain regions, mixed small-town + back-roads), and list the curated card subset to play with — including which base/expansion cards to include or pull, and any rural-specific cards authored on the blank stock.

> **Note (post cars-as-trains decision):** the rural variant now uses the original deck unchanged — see [`rules.md`](./rules.md) "Approach". The candidate deck-build sketches below were drafted under the older assumption that the ✗-marked transit-coupled curses would need replacement; treat them as historical context that needs a rewrite, not as live design proposals. The deck-builds idea itself may still be useful (e.g. for tuning by rural area type) but the cards-to-include/exclude logic has to be redone.

Why park this:

- The rural ruleset itself is still placeholder. Tuning a deck against rules that don't exist yet is premature.
- We don't yet have full mechanic text for every expansion card (see [`reference/cards.md`](./reference/cards.md) "Remaining gaps"), so we can't yet make informed include/exclude calls on the curse pool.
- The "kind of rural area" axis needs concrete play data or at least a worked example before becoming a stable taxonomy. Right now it's a guess about what dimensions matter.

Revisit once: rules have actual content. (Expansion card mechanics are now in hand — see [`reference/cards.md`](./reference/cards.md).)

### Candidate deck builds — first draft

These are **untested sketches**, not recommendations. They exist so the eventual `decks/` folder has somewhere to start instead of a blank page. Each build is a starting include/exclude list keyed off the markers in [`reference/cards.md`](./reference/cards.md). Rural rules don't yet exist, so distance rescaling and any new rural-specific curses (authored on the 25 base-deck blanks) are flagged as TODO inside each build rather than chosen.

The relevant axes a build is parameterized on:

- **Population density** — drives stranger / passer-by availability (Anonymous Benefactor, Bargain Hunter), commercial-place availability (4.3-star spots for Shrewd Critic, post offices for Post Office), and subject diversity (museums, restaurants).
- **Road network** — affects Right Turn (vehicle-feasible at any density), Grass-Toucher (gets *easier* in low-named-street country), Impenetrable Fog (same).
- **Terrain features** — coast / mountains / lakes affect Seabird, body-of-water photo questions.
- **Commercial-airport reach** — gates Planespotter (10-mile cast cost).
- **Cell + outlet coverage** — affects Landline (charging an outlet for two hours is much harsher in country with long no-building stretches).
- **Seeker count** — Mind Meld and Passenger Princess require ≥ 2 seekers; Hide-and-Seek-Ception requires ≥ 2 too.

Three candidate builds below. None are tuned; they are starting points for review.

#### 1. "County seat" build — small-town-anchored play

Targets a county with one or two small towns of low-thousands population and a rural-road network between them. Game radius assumed in the M tier (~15–30 miles).

- **Drop entirely (✗):** Gambler's Feet, Express Route, U-Turn, Urban Explorer, Long Shot, Freewheeler, Strider, Data Leak. All transit- or foot-locked; no clean rural port without rewriting them.
- **Adapt and keep (⚠):** Bridge Troll, Distant Cuisine, Mediocre Travel Agent, Impressionable Consumer, Jammed Door, Luxury Car, Unguided Tourist, Water Weight, Bargain Hunter, Curious Explorer, Plagued Word, Post Office, Seabird, Shrewd Critic, Anonymous Benefactor, Landline, Planespotter — each needs a distance / density rescale. TODO: pick rescale rules in [`rules.md`](./rules.md), then come back here.
- **Keep as-is:** the unmarked majority — skill challenges, communication restrictions, hider-economy curses, the photo curses without urban-density assumptions.
- **Multi-seeker only — flag when single-seeker:** Mind Meld, Passenger Princess, Hide-and-Seek-Ception.
- **Open question:** rural-specific blanks. The 25 blanks in the base deck are the design vector. Candidates: a vehicle-range / fuel-detour curse, a livestock-or-crop photo curse, a county-line-crossing detour, a sunset-time-pressure curse. Park the list here; commit when authored.

#### 2. "Backcountry" build — very-low-density play

Targets areas where towns are 30+ miles apart, no commercial airport in reach, sparse cell coverage. Game probably runs at L tier (~50+ mile radius).

- **Drop entirely (✗):** same set as County Seat, plus consider dropping **Planespotter** entirely if no commercial airport sits within the game radius (the casting cost can never be paid). Also flag **Anonymous Benefactor** and **Bargain Hunter** for likely cut — both depend on stranger / commercial-pricing density that may not exist.
- **Adapt aggressively (⚠):** distance buckets on detour-gating and movement-restriction curses likely need to be re-tiered upward beyond what the printed L values offer (the printed L of "10 miles" for Blind Wanderer, for example, may want to be 25 or 50 in true backcountry).
- **Lean into:** skill-challenge gating (Strongman, Oracle, Hidden Hangman, Pong Champion, Endless Tumble, etc.) — these decouple cleanly from geography and don't need rescaling.
- **Open question:** does the deck shrink, or do we replace the cut cards with rural-specific blanks one-for-one to keep deck composition stable?

#### 3. "Coastal / waterfront" build

Targets rural play where a coastline, large lake, or river system is a primary map feature.

- **Drop:** still the transit-/foot-locked set as County Seat.
- **Promote:** Seabird (water-side photo) becomes high-relevance and may want a copy added rather than removed; the body-of-water photo subjects in the Investigation Book matter more.
- **Open question:** whether to author a "boat / shoreline" detour-gating blank as a feature card.

---

### Calibration gap noted in `notes.md`

`notes.md` flags a `<!-- TODO -->` for size-tier complexity calibration: the official rulebook publishes target transit-station counts per game size (~30–100 / 100–500 / 500+), and rural play needs an analogous metric — number of valid hide anchors per square mile, or similar. Until that's chosen, a rural game's effective "size tier" can't be picked deterministically; deck builds above lean on subjective tier guesses ("M-ish for County Seat, L-ish for Backcountry"). Resolve calibration before treating any of the builds above as final.
