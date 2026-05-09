# Transit friction — research notes

Background research for the rural Hide + Seek variant: how does public transit produce *trip-making friction* (waiting, transferring, route topology, last-mile walks)? The original game leans on those frictions to shape seekers' decisions; a vehicle-based rural variant strips most of them out by default and so has to engineer artificial replacements.

> Original synthesis citing external academic sources. **Per-citation claims are facts from the cited paper; the framing and the rural-design implications are reasoned inference**, not measured findings — see [`./README.md`](./README.md) and [`../../CLAUDE.md`](../../CLAUDE.md) on the writing posture this file follows.

---

## Perceived-cost layer (what research has measured)

Transit users do not perceive all minutes equally. Travel-behaviour research decomposes a transit trip into components and weights each against in-vehicle time (IVT) as the base unit:

- **In-vehicle time** — weight 1.0 (baseline).
- **Walking time** (access from origin + egress to destination) — roughly **1.5× IVT** in disutility. Son et al. 2007 estimate the walk-time weight at 1.507 against IVT for inner-Seoul trips [6].
- **Waiting time** (initial + transfer waits) — roughly **1.75–2× IVT**. Son et al. 2007 find a waiting-time weight of 1.749 [6]; Petruccelli et al. 2021 find waiting weighted approximately twice in-vehicle time in regional Italian transit [1].
- **Pure transfer penalty (PTP)** — the disutility of changing vehicles *beyond* the additional walking and waiting it entails: equivalent to **13–18 extra in-vehicle minutes per transfer**. Jara-Díaz et al. 2022 propose 13–18 EIVM as a planning range across reviewed studies [3]; García-Martínez et al. 2018 estimate 15.2–17.7 EIVM in Madrid [4]; a meta-analytic figure of 17.6 EIVM is reported in [3]. Petruccelli et al. 2021 separately estimate ~3.5 minutes of additional perceived cost per transfer [1].
- **Equity / access asymmetry** — Lachapelle et al. 2023 (Montreal) find lower-income riders spend a greater share of total trip time in access + waiting because of where they live relative to high-frequency lines and a greater need to chain modes [2]. Same total trip time, slower effective speed, more off-vehicle time.

Iseki & Taylor 2009 [5] propose a five-attribute framework for transfer-facility quality (access, connection / reliability, information, amenities, security) that the per-component weights above all cash out into.

**The takeaway for game design:** the cost of a transit trip is dominated by the *off-vehicle* interruptions — waiting, walking, transferring — rather than the in-vehicle distance itself. Driving has almost none of those structurally. A rural / vehicle-based adaptation that wants comparable per-trip friction has to manufacture analogues to walking, waiting, and transfer-interruption — not just analogues to in-vehicle motion such as range limits.

---

## Operational layer (what transit *does* that produces cost)

A complementary view: the operational features of transit that produce the perceived costs above. Roughly ordered by how strongly each shapes seekers' route choice in a Hide + Seek-style game.

1. **Network topology.** The graph constrains paths. Going from A to B may force passage through hub C. Hub-and-spoke, radial, and grid networks produce different "you can't get there directly" effects. Petruccelli et al. 2021 frame this as the trade-off between feeder-trunk integration (more transfers, more rides per mile) and direct-link patterns (fewer transfers, less coverage) [1].
2. **Headway / wait time.** The gap between vehicles. In heavily-served urban systems peak headways can drop to a few minutes; off-peak headways on suburban or low-frequency services commonly stretch to 15–30+ minutes (general — verify per-system before quoting specific numbers). Doubles to triples the perceived cost of any short trip via the ~1.75–2× wait-time weight [1, 6].
3. **Transfer penalty.** Every line change adds ~13–18 EIVM beyond the literal walk + wait [3, 4]. The largest single piece of "synthetic" friction in a multi-leg trip.
4. **Last-mile walk.** Station to actual destination, weighted ~1.5× IVT [6]. Forces a foot-mode segment, slows fine-grained location work, makes off-network destinations expensive in disutility terms.
5. **Operating hours / span of service.** Last-train / first-train windows; weekend service reductions; no-service overnight windows. Verify per-system.
6. **Route commitment.** Once boarded — especially on express service — disembarking until the next stop is not an option. Loop and one-way segments enforce direction. (Operationally observable, not measured in the surveyed papers.)
7. **Service-area coverage.** The network only covers part of the map. Outer zones often require chaining a low-frequency feeder bus to a trunk line, compounding waits and transfers. Lachapelle et al. 2023 link this to the equity finding above [2].
8. **Disruptions.** Engineering works, weather, incidents. Stochastic friction; a route that worked yesterday may not exist today.
9. **Information availability.** Iseki & Taylor 2009 treat schedule / route information as part of the access-cost component [5] — not knowing when the next vehicle arrives is itself a cost.
10. **Comfort / crowding.** Treated in the literature as a multiplier on IVT (a full bus during rush hour feels longer than it is) [4]. Less directly translatable to a Hide + Seek-style design.

---

## Implications for the rural variant *(inference, not measured)*

A vehicle-only rural variant strips out most of categories 1, 3, 4, 5, and 6 by default. The road network is dense and routable in many directions; seekers don't transfer; they don't wait; they don't walk a last mile to reach a building; pull-over is possible almost anywhere. **Vehicle range is the only naturally-occurring constraint, and it sits closest to category 5 (operating hours / span of service)** — a temporal-budget cap.

If the design goal is to recreate the trip-shaping pressure transit imposes, range alone is unlikely to be enough. The candidate moves below map each transit-friction category to a possible driving-side analogue. They are starting points for design, not recommendations.

| Transit friction category | Candidate driving analogue |
|--------------------------|----------------------------|
| Network topology (1) | Forced waypoints — must pass through county seats, named junctions, or other anchors before continuing. |
| Headway / wait time (2) | Mandatory dwells — must remain at a location class (gas station, town square, fixed checkpoint) for N minutes before resuming. |
| Transfer penalty (3) | Vehicle-class swap or check-in rituals at dwell sites; explicit "pass-through-X" fees in the action economy. |
| Last-mile walk (4) | Photo / proof-of-presence requirements — must dismount and capture a pedestrian-scale object (a sign, a doorway) before the question counts. |
| Operating hours (5) | Vehicle range cap; daylight-only seeking; no-drive windows tied to time of day. |
| Route commitment (6) | Cooldowns on road-segment reuse — same segment cannot be re-driven within N hours; once committed to a county-road, exit only at named junctions. |
| Service-area coverage (7) | Off-network penalties — entering certain map regions costs draws or time, modeling the "bus-to-train chain" friction. |
| Disruptions (8) | Stochastic delay cards — drawn periodically, force detours or dwells. |

The replacement-card design exercise in [`../design-backlog.md`](../design-backlog.md) should probably be re-grounded against this taxonomy when it resumes: each ✗-marked card needs a replacement that produces friction in *one of the categories above*, rather than just a vehicle-flavoured rewrite of the original mechanic.

---

## References

[1] [Feeder-trunk and direct-link schemes for public transit: a model to evaluate the produced accessibility](https://consensus.app/papers/details/f99aa7c1805d5bcc8ffa2d5a79f9dc3c/?utm_source=claude_code) — Petruccelli, U., et al. (2021), *Public Transport*. Cited for: regional Italian transit, waiting-time ≈ 2× IVT, transfer-time ≈ 1.5× IVT, ~3.5 min per-transfer disutility, feeder-trunk vs direct-link framing.

[2] [Breaking down public transit travel time for more accurate transport equity policies: A trip component approach](https://consensus.app/papers/details/070c462b1f8d5670ab69f38be3c6679a/?utm_source=claude_code) — Lachapelle, U., et al. (2023), *Transportation Research Part A: Policy and Practice*. Cited for: income / access-time equity findings; trip-component decomposition (Montreal data).

[3] [An international time equivalency of the pure transfer penalty in urban transit trips: Closing the gap](https://consensus.app/papers/details/6336f2b5cb005c2f857f09869d39cb26/?utm_source=claude_code) — Jara-Díaz, S., et al. (2022), *Transport Policy*. Cited for: 13–18 EIVM PTP planning range; meta-analytic 17.6 EIVM figure.

[4] [Transfer penalties in multimodal public transport networks](https://consensus.app/papers/details/8d3a171a2b015297a3d4984b33cb0c6b/?utm_source=claude_code) — García-Martínez, A., et al. (2018), *Transportation Research Part A: Policy and Practice*. Cited for: 15.2–17.7 EIVM PTP estimate (Madrid); crowding multiplier on IVT.

[5] [Not All Transfers Are Created Equal: Towards a Framework Relating Transfer Connectivity to Travel Behaviour](https://consensus.app/papers/details/2709006bd00757e3a9f9157f98091f01/?utm_source=claude_code) — Iseki, H. & Taylor, B. D. (2009), *Transport Reviews*. Cited for: five-attribute transfer-facility framework (access / connection / information / amenities / security).

[6] [An Estimation of Generalized Cost for Transit Assignment](https://consensus.app/papers/details/a76adb471c515575964e3c0b63ae5cfd/?utm_source=claude_code) — Son, S., et al. (2007), *Journal of the Eastern Asia Society for Transportation Studies*. Cited for: Seoul-data weights — walk 1.507× IVT, wait 1.749× IVT, transfer 1.474× IVT.
