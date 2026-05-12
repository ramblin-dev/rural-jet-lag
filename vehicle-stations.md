# Vehicle stations — cross-game mechanic

The single shared mechanic that all rural Jet Lag adaptations in this repo are built on. Each per-game directory (`hide-and-seek/`, future `tag/`, etc.) defines its own rules but adapts only the *transportation layer* — and that layer is the same idea everywhere: **personal vehicles, ride-sharing, and taxis play the role of buses and trains, anchored to a generated set of "vehicle stations" with a wait-time roll on every departure.** Real bus / train / ferry service in your play area, if any, plays per the official rulebook alongside vehicle stations.

This file is the canonical write-up of that idea. Per-game `rules.md` files reference it instead of restating it.

---

## Why this mechanic exists

Jet Lag: The Game leans on the friction of public transit — waiting for the next train, transferring between lines, walking the last block — to shape interesting decisions for both seekers and hiders. In rural environments where the buses don't run and the nearest train station is in the next state, that friction disappears the moment players get in a car. Free driving is too fast and too unconstrained, and a "fuel budget" alone doesn't reproduce the *temporal* texture of transit (the unpredictable wait, the choice of where to transfer).

The vehicle-stations mechanic re-introduces transit-shaped friction without requiring transit infrastructure. Cars become the buses; clustered points-of-interest become the stations; a 2d6 departure roll becomes the schedule. Background research and per-component cost weights live in [`hide-and-seek/reference/transit-friction.md`](./hide-and-seek/reference/transit-friction.md).

---

## What a vehicle station is

A vehicle station is a real-world location — a museum, park, gas station, restaurant, etc. — that the [`tools/generate_vehicle_stations.py`](./tools/) script picked from OpenStreetMap inside your play-area polygon. Each station carries:

- **Coordinates** — for display in Google My Maps or any KML-capable map app.
- **A category** — what kind of POI it is (museum, café, gas station, …).
- **A cluster id** — which "town" or commercial area it belongs to.
- **A wait-time range** — derived from local POI density, three tiers:
  - **Dense** (≥15 POIs within ~1 mile): 5–15 min
  - **Moderate** (5–14): 10–30 min
  - **Sparse** (0–4): 20–60 min

Stations are spaced using a two-tier rule: ~300 m minimum within a cluster (matching average urban bus stop spacing), ~1000 m minimum between clusters (matching light-rail / metro spacing). The result on the map is groups of stations around towns and commercial areas with visible gaps between them — the same shape transit stops take in real cities.

See [`tools/README.md`](./tools/) for how to generate the station map for your play area.

---

## How vehicle stations fit alongside bus and train lines

Any rule in the official Jet Lag rulebooks that references transit translates as follows:

| Official term | Rural-variant reading |
|---|---|
| Bus / train / metro stop | Vehicle station |
| Bus / train line | Real lines that exist in your area (a small-town bus, a tourist trolley, an Amtrak run) play as the official rulebook describes them — the rural variant adds no special rules for them. The rural mechanic only changes how *cars* move. |
| Boarding a vehicle | Driving away from a station after the wait clears |
| Schedule wait | The 2d6 departure roll at the station that starts a route |
| Transfer | Ending one route at a station and declaring a new one (with its own roll) |
| End of the line | The last station in your declared route |

What this preserves: every change in plan incurs a wait, longer trips amortize fewer rolls per mile (so they "run faster" the same way long transit lines do), and transfers cost real time. What you gain: stations are picked from places you'd actually want to visit (parks, museums, cafés, bookstores) rather than the real-world stops a transit agency optimized for route and passenger efficiency, so the station map tends to be more interesting to play across. What you lose: pre-fixed lines and timetables — every station connects to every other station, and the schedule is rolled fresh per departure.

---

## The departure roll

Every route begins with a departure roll at its starting station, *before* you drive anywhere. Roll **2d6** and read the sum against the station's wait-time range:

| 2d6 sum | Outcome | Probability | Example for 10–15 min range |
|--------:|---------|------------:|------------------------------|
| 2–3 | **On time.** Leave immediately. | 8.3 % | Leave now |
| 4–6 | **Lower bound** of the range. | 33.3 % | 10 min |
| 7–10 | **Upper bound** of the range. | 50.0 % | 15 min |
| 11–12 | **You missed your departure.** Wait the upper bound, then re-roll. | 8.3 % | Wait 15 min, then re-roll for a new departure |

The skew toward the upper bound is intentional — real transit runs late more often than early, so the dice carry that bias forward. This skew is a design choice, not a measured calibration target, and is tunable along with the rest of the table.

You leave a station by **driving off in your vehicle.** If you don't drive off within your rolled wait time, you've missed your departure. Roll again for the next one — including the chance of another miss on an 11 or 12.

---

## Routes

A **route** is a pre-declared sequence of stations from your current location to your destination. Most routes will include intermediate stations between the two ends.

- **A route's declared sequence cannot include the same station twice** — every station in the sequence must be distinct.
- **You may pass any intermediate station along your declared route without pulling over.**
- **You must stop at the destination station you declared.** That is the end of your route.
- **You must get out of your vehicle before declaring or rolling for the next route.** Stretching your legs and actually looking at the place counts; staying buckled in does not. This applies at every route end: destination stops, mid-route change points, and the start of the very first route of the day.

Why the dismount rule: vehicle stations are picked from places that are interesting to be at — parks, museums, cafés, bookstores, arcades. Without a get-out requirement the station becomes a math token on a map. Forcing a brief dismount turns each stop into a reason to actually take a look at the site, which is half the point of choosing those POIs in the first place.

Why the destination is a forced stop (separately from the dismount): without it, players could declare a route ending at the next station they're already approaching, hop through with no roll, declare another, and effectively never incur a departure roll. The forced stop ensures every route imposes at least one roll's worth of friction. Short routes get to that roll sooner, so they incur more total rolls per mile traveled; long routes amortize the friction over a longer commitment.

### Changing your route mid-trip

A mid-route change is just ending your current route early and starting a new one from there:

1. Pick a station along your current route to be your new endpoint. Treat it as your destination from this point forward.
2. Drive there. That station is the end of your current route.
3. **Get out of the vehicle.** As above.
4. From that station, declare a new route to wherever you want to go next. Make a departure roll for the new route, as you would for any route.
5. Once your wait clears, drive off on the new route.

There is no separate "transfer" mechanic — a mid-route change is just two routes back-to-back, each with its own declaration, dismount, and departure roll.

---

## By-request transport (ride-sharing, taxis, hotel shuttles)

Some play areas have no real transit, or no players with personal vehicles, but do have on-demand ride options — Uber, Lyft, Via, local taxi services, hotel shuttles, etc. These play under the basic mechanic with one allowance: you may time your ride request so the vehicle arrives at the end of your rolled wait.

When you're ready to leave a station by by-request transport:

1. **Declare your route** and make a normal 2d6 departure roll against the starting station's wait-time range.
2. **Wait the rolled time.** During the wait you may check ride-app ETAs as often as you like, but don't request the ride yet.
3. **Time the request** so the vehicle is scheduled to arrive at the station no earlier than the end of your rolled wait. (In practice: when the app's quoted ETA equals the time remaining on your wait, request the ride.)
4. The ride picks you up and you depart on your declared route.

> **Why timing the request is allowed.** Without it, by-request riders would be double-penalized — once for the station roll, once for the ride to arrive. Letting the rider line up the two waits keeps total time-to-vehicle-arrival roughly equal to the rolled wait, the same friction shape as transit.

**Changing your mind before requesting** — you may switch services, switch destination, or call off the trip entirely *up until you actually request the ride*. Doing so counts as a **missed departure** and requires a fresh departure roll. Once requested, the ride is committed and you ride it to the destination you declared.

### Mixing transport modes in one game

The mechanic is mode-agnostic, so any combination works:

- **Personal vehicles only** — the default rural framing.
- **Ride-sharing / taxis only** — for groups without access to a car, or for urban-edge play.
- **Personal vehicles + ride-sharing** — drive long legs, hail rides inside town.
- **Real transit + ride-sharing** — use a real bus line where it exists, fall back to Uber elsewhere.
- **All three** — real transit + personal vehicles + by-request transport.

Each mode resolves at the station the same way: declare → roll → wait → depart. Personal vehicles use the basic mechanic above; by-request transport adds the ride-timing allowance; real bus / train / ferry lines follow the official rulebook unchanged.

---

## What this mechanic doesn't change

The vehicle-stations layer governs how *non-transit vehicles* (personal cars, ride-sharing, taxis) move and nothing else. It does not by itself re-balance:

- The official rulebook's card decks, question books, or scoring.
- Game-size tiers (S/M/L) or any time-budget mechanics specific to a format.
- Hider mechanics (hiding zones, end-game triggers, found conditions in Hide + Seek; equivalents in Tag, etc.).

Per-game `rules.md` files are responsible for spelling out how their format handles the few official mechanics that do depend on transit topology (e.g. "end of the line" wording in Hide + Seek's Curse of the Express Route). Those caveats live with the format that needs them, not here.

---

## Tunability

All of the numbers above are starting points, not measured calibration targets. The tool exposes the spacing parameters as CLI flags, and the wait-tier breakpoints + 2d6 outcome table are constants near the top of [`tools/generate_vehicle_stations.py`](./tools/generate_vehicle_stations.py). If you find that play-tests want denser station maps, looser cluster spacing, longer waits in sparse areas, or a different miss probability — change them. The framing the rest of this file describes does not depend on the specific numbers.
