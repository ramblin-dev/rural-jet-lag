# Rural Hide and Seek — Rules

<!-- repo-only -->
> Part of [Rural Jet Lag](../README.md). For setup instructions (drawing a play area, generating vehicle stations, importing to Google Maps, etc.) see [`setup.md`](./setup.md).

> **Disclaimer:** This is an unofficial fan project. Not affiliated with Jet Lag: The Game, Nebula, or Wendover Productions. The official Hide + Seek rulebook, card text, and Investigation Book are © Wendover Productions / Nebula. You'll need your physical copy of the official game to play — see the [Before you play](../README.md#before-you-play) section of the top-level README for where to buy it.
<!-- /repo-only -->

---

## Approach

The rural variant changes only one thing about Hide + Seek: **how seekers (and the hider, while traveling to their hiding zone) travel between vehicle stations.** Travel by personal vehicle, ride-sharing, or taxi is required to behave like a bus or train via the [vehicle-stations mechanic](../vehicle-stations.md) — pre-declared routes between generated stations, with a 2d6 departure roll on every trip. By-request transport (Uber, Lyft, taxis, hotel shuttles) plays under the same roll, with the allowance that the rider can time the ride request so the vehicle arrives at the end of the rolled wait — see the cross-game write-up. Real bus or train lines in your play area, if any, still play per the official rulebook alongside vehicle stations; modes can be mixed freely within a single game. That cross-game write-up is the canonical reference for stations, routes, departure rolls, mid-route changes, and the by-request variant; this file covers only the Hide + Seek-specific application.

This approach **preserves the rest of the official rulebook unchanged**. In particular, no card replacements are needed:

- The hider deck (curses, power-ups, time bonuses) plays as printed.
- The hiding zone is centered on a vehicle station with the standard radius — same anchor mechanic as the original.
- The Investigation Book, end-game trigger, "found" condition, time-bonus scoring, hand limits, and casting costs are all unchanged.

The rural variant therefore **does not use the official "Playing Without Public Transit" experimental design** (the cars / on-foot variant in the rulebook, which replaces transit with free-form driving and street-terminus hiding zones). That variant takes a different approach to the same problem; applying both at once would compound them. Pick one or the other.

---

## Transportation

The shared transportation mechanic — what a vehicle station is, how to declare a route, how the 2d6 departure roll works, how missed departures and mid-route changes resolve — lives in [the cross-game vehicle-stations write-up](../vehicle-stations.md). Read that first; everything below is the Hide + Seek-specific overlay.

### Who it applies to, and when

The cross-game transportation rules apply to:

- **Seekers** throughout the seeking phase.
- **The hider** while traveling to their chosen hiding zone (i.e. before the hide period begins).

Once the hider arrives at their zone, transportation rules no longer apply to them — see [Hiding zone and other rules](#hiding-zone-and-other-rules) below for hider movement after that point.

### Departure rolls and round boundaries

In addition to the cases listed in [the cross-game departure-roll rules](../vehicle-stations.md#the-departure-roll), seekers must make a fresh departure roll for **their first route after a new round begins** — even if they remained in their vehicle the whole time between rounds. The round transition resets the rule's "every route begins with a roll" clock.

### Route privacy

Seekers do not share their declared route with the hider by default — the seeker team is trusted to follow the route they committed to. The Vol. 1 *Data Leak* curse, when in play, is what forces route-sharing on top of the default.

### Watching the phone while moving

Seekers always have at least two players, so the non-driving seeker watches the phone continuously and can read curses or other messages from the hider while the team is on the move. There is no need to pull over at intermediate stations to check messages.

---

## Hiding zone and other rules

For everything outside transportation, **follow the official Hide + Seek rulebook unchanged.** This includes:

- The hiding zone (anchor station, radius, valid hiding spots inside).
- Hider movement inside the zone.
- The end-game trigger when the seekers cross into the hiding zone off-vehicle.
- The "found" condition that resolves the round.
- Time-bonus scoring at end of round.
- The Investigation Book and all question categories.
- Card mechanics (hider deck, hand limits, casting costs).
- Map borders and the S/M/L game-size tiers.

You'll need your physical rulebook for the canonical wording.<!-- repo-only --> Structural reference (paraphrased, no quotes) is in [`reference/notes.md`](./reference/notes.md).<!-- /repo-only -->

---

## Caveats from the cars-as-trains framing

A few of the Vol. 1 expansion cards and a handful of Investigation Book questions need a one-line interpretation note in the rural variant. None require replacement.

- **Curse of the Express Route** — read its "unless they've reached the end of a line" wording as "unless they've reached the end of their declared route." There are no fixed transit lines in the rural variant.
- **Curse of Strider** and **Curse of the Gambler's Feet** — both are foot-only mechanics. They still play as written, but they only fire while seekers are on foot (e.g., walking through a town center after parking). In rural play that happens less often than in the original game.
- **Investigation Book — transit-anchored question subjects.** Subjects like "transit line," "high-speed train line," "rail station," and "station-name length" don't exist in most rural areas. Treat them as missing subjects, the same way the official rulebook handles any subject your map doesn't have. Commercial airports often *do* exist in rural game areas; questions about them apply normally.

If a future rural-specific change to the rest of the ruleset turns out to be necessary, it will be added here. Until then, this section is the full list of deltas from the official game.
