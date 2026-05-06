# Transportation Mechanics

> Part of the [Rural Hide and Seek Ruleset](./README.md)

---

## Core Change: Transit → Driving

In the original Hide and Seek format, players are constrained by the transit network — they can only move between points connected by a bus line, subway, or train. In the rural variant, **personal vehicles replace transit entirely**.

---

## Rules

### 1. Primary Mode of Travel
- All players travel by **personal vehicle** (any car, truck, or SUV — gas, hybrid, or electric).
- No rideshares or ride-hailing services count as valid moves unless both teams agree in advance.
- Walking and cycling are allowed but are rarely strategic given the map scale.

### 2. Road Networks Replace Transit Lines
- Movement is constrained by **the road network**, not a transit map.
- Players may travel any public road (paved or gravel) within the play area.
- Private roads and gated land are off-limits unless the landowner has given permission.

### 3. Driving Time Isochrones Replace Transit Zones
- In urban play, "zones" are defined by transit stop proximity. Here, zones are defined by **driving-time isochrones** — areas reachable within a set drive time from a reference point.
- Suggested zone thresholds:
  - **Zone 1:** 0–15 minutes of driving
  - **Zone 2:** 15–30 minutes of driving
  - **Zone 3:** 30–60 minutes of driving
  - **Zone 4:** 60–90 minutes of driving (outer boundary of most games)
- See [`tools/`](../tools/) for a script that generates these isochrones automatically.

### 4. Speed Assumptions
- Assume an average driving speed of **45 mph on county roads** and **65 mph on state/US highways**.
- Do not assume traffic; rural roads are rarely congested.
- Seasonal road closures (muddy roads, flooded crossings) are fair game — inform all players of known closures before the game starts.

### 5. Stops & Refueling/Recharging
- Players may stop to refuel or recharge during play. Stop time counts as game time.
- Fueling and charging station stops can be used strategically — a Hider can delay a Seeker by hiding near the only fueling or charging station in a large area.

### 6. Crossing Boundaries
- Crossing a defined boundary (county line, river, state line) may only be done if a **Crossing Card** is played from a player's hand.

---

## Suggested Map Tools

Use [OpenRouteService](https://openrouteservice.org/) or the script in [`tools/driving_isochrone.py`](../tools/driving_isochrone.py) to pre-generate isochrone maps for your play area before the game starts. Print or share the map with all players.

---

*See also: [Range Budgeting](./budgeting.md) | [Geography & Hiding](./geography.md) | [Full Ruleset](./full-ruleset.md)*
