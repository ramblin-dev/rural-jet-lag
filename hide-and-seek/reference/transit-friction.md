# Transit friction — research notes

Background research for the rural Hide + Seek variant: how does public transit produce *trip-making friction* (waiting, transferring, route topology, last-mile walks)? The original game leans on those frictions to shape seekers' decisions; a vehicle-based rural variant strips most of them out by default and so has to engineer artificial replacements.

> Original synthesis citing external academic sources. **Per-citation claims are facts from the cited paper; the framing and the rural-design implications are reasoned inference**, not measured findings — see [`./README.md`](./README.md) and [`../../CLAUDE.md`](../../CLAUDE.md) on the writing posture this file follows.

---

## Perceived-cost layer (what research has measured)

Transit users do not perceive all minutes equally. Travel-behaviour research decomposes a transit trip into components and weights each against in-vehicle time (IVT) as the base unit:

- **In-vehicle time** — weight 1.0 (baseline).
- **Walking time** (access from origin + egress to destination) — roughly **1.5× IVT** in disutility. Son et al. 2007 estimate the walk-time weight at 1.507 against IVT for inner-Seoul trips [6].
- **Waiting time** (initial + transfer waits) — roughly **1.75–2× IVT**. Son et al. 2007 find a waiting-time weight of 1.749 [6]; Petruccelli et al. 2021 find waiting weighted approximately twice in-vehicle time in regional Italian transit [1].
- **Pure transfer penalty (PTP)** — the disutility of changing vehicles *beyond* the additional walking and waiting it entails. Reported in **Equivalent In-Vehicle Minutes (EIVM)**: how many extra minutes of in-vehicle time would feel equivalent in disutility to the cost of one transfer. (Riders don't actually spend that long mid-transfer — EIVM is a perceived-cost equivalency, not a clock-time measurement.) Across studies the planning range is **13–18 EIVM per transfer**. Jara-Díaz et al. 2022 propose 13–18 EIVM as a planning range across reviewed studies [3]; García-Martínez et al. 2018 estimate 15.2–17.7 EIVM in Madrid [4]; a meta-analytic figure of 17.6 EIVM is reported in [3]. Petruccelli et al. 2021 separately estimate ~3.5 minutes of additional perceived cost per transfer [1].
- **Equity / access asymmetry** — Lachapelle et al. 2023 (Montreal) find lower-income riders spend a greater share of total trip time in access + waiting because of where they live relative to high-frequency lines and a greater need to chain modes [2]. Same total trip time, slower effective speed, more off-vehicle time.

Iseki & Taylor 2009 [5] propose a five-attribute framework for transfer-facility quality (access, connection / reliability, information, amenities, security) that the per-component weights above all cash out into.

**The takeaway for game design:** the cost of a transit trip is dominated by the *off-vehicle* interruptions — waiting, walking, transferring — rather than the in-vehicle distance itself. Driving has almost none of those structurally. A rural / vehicle-based adaptation that wants comparable per-trip friction has to manufacture analogues to walking, waiting, and transfer-interruption — not just analogues to in-vehicle motion such as range limits.

---

## Actual time costs and modal speeds (observed, not perceived)

The perceived-cost layer above is about how riders *experience* time. This section is about how much time actually elapses on the clock — what trip-makers measure with a stopwatch. Both layers matter for game calibration: perceived cost shaped the original game's curse design (transfer-style penalties feel justified because they hurt), but actual time determines how fast seekers can physically reach the hider.

### Door-to-door PT-vs-car travel time ratio

Liao et al. 2020 [7] ran a four-city comparison (São Paulo, Sydney, Stockholm, Amsterdam) using real-time traffic + transit data:

- **Transit takes 1.4–2.6× longer than driving on daily average** across the four cities.
- The PT/car travel-time ratio is **low for trips under ~3 km, then increases rapidly and stabilizes near 2.0** for longer trips. The pattern is "surprisingly similar across cities."
- Only **0.4–1.2% of city area** is faster by transit than by car — daily and during peak hours.

Salonen et al. 2013 [8] (Helsinki) corroborate that door-to-door modeling matters: simplified comparisons that ignore parking, congestion, schedule waiting, and walking will distort the gap. Modal disparity is smallest in dense city centers and grows outward.

Durán-Hormazábal et al. 2016 [9] (Santiago) decompose **door-to-door variability**: bus waiting time and in-vehicle time dominate, and buses in mixed traffic have both higher mean travel time and higher variability than buses on segregated busways. Metro travel time is generally more stable.

### Commercial / operating speeds by mode

Speeds reported as average end-to-end including stops:

| Mode | Commercial speed | Source |
|------|-----------------:|--------|
| Fully-segregated metro | 30–40 km/h (~19–25 mph) | Allport 2011 [10] |
| Partly-segregated light rail | ~20 km/h (~12 mph) | Allport 2011 [10] |
| BRT / busway | 17–24 km/h (~11–15 mph) | Allport 2011 [10]; Hidalgo et al. 2013 [11] |

For comparison, **typical rural driving** (county roads + occasional highway, US context) is roughly 45–65 mph (72–105 km/h). Highway-heavy rural runs go higher.

### Implied speed gap

Rural driving is about **2–3.5× faster per minute** than urban transit's commercial speed — and that's before adding the access / wait / transfer time that grows the door-to-door gap to the ~2× ratio Liao et al. measure [7]. For the rural variant, this means:

- A seeker who drives unconstrained in rural play moves roughly **2–4× faster than the original game's implicit transit-bound seeker** would over a trip of equivalent distance.
- Rural rules that want to preserve the original game's pacing need to slow seekers' *effective* speed by a comparable factor — through artificial friction, not just by capping vehicle range.

This is reasoned inference from the modal-speed and door-to-door numbers; it is not a measured calibration.

### Density thresholds for cost-effective transit

Cervero & Guerra 2011 [12] (US light-rail and heavy-rail systems) find density thresholds for transit to land in the top quartile of cost-effective investments:

- **~30 people per gross acre near stations** for light rail (≈ 19,200 people/mi²).
- **~45 people per gross acre near stations** for heavy rail (≈ 28,800 people/mi²).

For reference, US rural counties are typically under 100 people/mi², small towns under 5,000 people/mi², dense urban cores 25,000+ people/mi². **Rural areas sit two-to-three orders of magnitude below the densities at which fixed-route transit can be cost-recoverable** — explaining structurally why no transit exists to adapt around. The rural variant is not "behind" on transit; it occupies a regime where transit is fundamentally not a viable mode.

### Walking-access distances

Taylor et al. 2024 [13] (Melbourne) distinguish **acceptable walking distance (AWD)** — a minimum-coverage standard for service planning — from **tolerable walking distance (TWD)** — the maximum people will actually walk. They fit walking-access distance distributions with a Burr Type XII function and find AWD/TWD vary by city and population subgroup. (Common rule-of-thumb thresholds in the planning literature: ~400m for bus, ~800m for rail; verify per-region before quoting.) Li et al. 2022 [14] (Nanjing) show catchment areas for the same access mode differ between urban and suburban contexts.

### Service-frequency / ridership elasticity

Berrebi et al. 2021 [15] (US: Portland, Miami, Minneapolis–St-Paul, Atlanta) find ridership elasticity to frequency is **elastic between routes** at a single point in time (the most frequent routes are the most productive per vehicle-trip) but **inelastic within a route over time** (each added vehicle-trip generates less marginal ridership). Low-frequency routes are the most sensitive to frequency changes. The take-away for design: friction-reduction has diminishing returns above a baseline service level — the first few minutes of headway reduction matter much more than the last few.

---

## Operational layer (what transit *does* that produces cost)

A complementary view: the operational features of transit that produce the perceived costs above. Roughly ordered by how strongly each shapes seekers' route choice in a Hide + Seek-style game.

1. **Network topology.** The graph constrains paths. Going from A to B may force passage through hub C. Hub-and-spoke, radial, and grid networks produce different "you can't get there directly" effects. Petruccelli et al. 2021 frame this as the trade-off between feeder-trunk integration (more transfers, more rides per mile) and direct-link patterns (fewer transfers, less coverage) [1].
2. **Headway / wait time.** The gap between vehicles. In heavily-served urban systems peak headways can drop to a few minutes; off-peak headways on suburban or low-frequency services commonly stretch to 15–30+ minutes (general — verify per-system before quoting specific numbers). Doubles to triples the perceived cost of any short trip via the ~1.75–2× wait-time weight [1, 6].
3. **Transfer penalty.** Every line change adds a perceived cost of ~13–18 EIVM beyond the literal walk + wait [3, 4] — see the perceived-cost layer above for what EIVM means. The largest single piece of "synthetic" friction in a multi-leg trip.
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

### Toward density- and distance-parameterized rules *(inference)*

The actual-cost numbers above suggest a calibration framework that does not require bespoke per-region rule tuning. Three load-bearing ideas:

1. **Target effective seeker speed, not raw speed.** If the original game implicitly assumes seekers move at urban-transit door-to-door pace (commercial speeds ~10–25 mph for the underlying mode [10, 11], inflated to ~2× car-equivalent over trips longer than ~3 km [7]), then the rural-variant calibration target is a **seeker effective speed comparable to that** — not free-form rural driving at 50+ mph. Artificial friction (mandatory dwells, forced waypoints, segment-reuse cooldowns) should be sized to bring effective speed down to roughly the speed the original game implicitly assumed.
2. **Parameterize friction intensity on density.** Cervero & Guerra's density thresholds [12] mean rural play occupies a regime where transit is structurally absent. The intensity of artificial friction the rural variant imposes can be parameterized on local density — denser rural regions (small-town corridors) can borrow more from the original game's mechanics with rescaled distances; very low-density regions (open backcountry) need stronger artificial friction because rural driving speeds are highest there. A function of the form `friction_factor = f(population_density, distance_between_anchors)` is the structural shape — specific coefficients require playtesting.
3. **Bucket distances by game-size tier rather than by absolute distance.** The original game's three size tiers (S/M/L) already encode a distance bucket scheme: a "1-mile" radius means something different at S than at L. The rural variant can re-pick those bucket values per tier so that, e.g., a "Radar" question's 1-mile-equivalent in rural-L is whatever distance corresponds to the same fraction-of-game-radius the original 1 mile covered in transit-L. This avoids per-region rule tuning by absorbing geographic variation into tier choice.

What this approach buys: a small set of universal rules with two or three parameters keyed to local conditions, instead of a separate ruleset for "Iowa farmland" vs "Vermont mountains" vs "Nevada desert." What it costs: every parameter that gets pushed to the player adds setup friction. Worth pricing the trade-off explicitly when the rural rules in [`../rules/`](../rules/) get drafted.

---

## References

[1] [Feeder-trunk and direct-link schemes for public transit: a model to evaluate the produced accessibility](https://consensus.app/papers/details/f99aa7c1805d5bcc8ffa2d5a79f9dc3c/?utm_source=claude_code) — Petruccelli, U., et al. (2021), *Public Transport*. Cited for: regional Italian transit, waiting-time ≈ 2× IVT, transfer-time ≈ 1.5× IVT, ~3.5 min per-transfer disutility, feeder-trunk vs direct-link framing.

[2] [Breaking down public transit travel time for more accurate transport equity policies: A trip component approach](https://consensus.app/papers/details/070c462b1f8d5670ab69f38be3c6679a/?utm_source=claude_code) — Lachapelle, U., et al. (2023), *Transportation Research Part A: Policy and Practice*. Cited for: income / access-time equity findings; trip-component decomposition (Montreal data).

[3] [An international time equivalency of the pure transfer penalty in urban transit trips: Closing the gap](https://consensus.app/papers/details/6336f2b5cb005c2f857f09869d39cb26/?utm_source=claude_code) — Jara-Díaz, S., et al. (2022), *Transport Policy*. Cited for: 13–18 EIVM PTP planning range; meta-analytic 17.6 EIVM figure.

[4] [Transfer penalties in multimodal public transport networks](https://consensus.app/papers/details/8d3a171a2b015297a3d4984b33cb0c6b/?utm_source=claude_code) — García-Martínez, A., et al. (2018), *Transportation Research Part A: Policy and Practice*. Cited for: 15.2–17.7 EIVM PTP estimate (Madrid); crowding multiplier on IVT.

[5] [Not All Transfers Are Created Equal: Towards a Framework Relating Transfer Connectivity to Travel Behaviour](https://consensus.app/papers/details/2709006bd00757e3a9f9157f98091f01/?utm_source=claude_code) — Iseki, H. & Taylor, B. D. (2009), *Transport Reviews*. Cited for: five-attribute transfer-facility framework (access / connection / information / amenities / security).

[6] [An Estimation of Generalized Cost for Transit Assignment](https://consensus.app/papers/details/a76adb471c515575964e3c0b63ae5cfd/?utm_source=claude_code) — Son, S., et al. (2007), *Journal of the Eastern Asia Society for Transportation Studies*. Cited for: Seoul-data weights — walk 1.507× IVT, wait 1.749× IVT, transfer 1.474× IVT.

[7] [Disparities in travel times between car and transit: Spatiotemporal patterns in cities](https://consensus.app/papers/details/6f880e46d6035cada75bf0571f5744b6/?utm_source=claude_code) — Liao, Y., et al. (2020), *Scientific Reports*. Cited for: PT/car door-to-door ratio 1.4–2.6× across São Paulo / Sydney / Stockholm / Amsterdam; ratio stabilizes near 2.0 for trips over ~3 km; only 0.4–1.2% of city area faster by transit.

[8] [Modelling travel time in urban networks: comparable measures for private car and public transport](https://consensus.app/papers/details/1ba34230c43559e49fbd1907c2875704/?utm_source=claude_code) — Salonen, M. & Toivonen, T. (2013), *Journal of Transport Geography*. Cited for: methodological framework for door-to-door PT-vs-car comparison (Helsinki); modal disparity smallest in city-center.

[9] [Estimation of travel time variability for cars, buses, metro and door-to-door public transport trips in Santiago, Chile](https://consensus.app/papers/details/f012539ef0325eef9bbc8dd32e543cba/?utm_source=claude_code) — Durán-Hormazábal, E. & Tirachini, A. (2016), *Research in Transportation Economics*. Cited for: door-to-door variability decomposition; bus mixed-traffic vs busway differences.

[10] [Rail Rapid Transit Advances](https://consensus.app/papers/details/c06c31a879f4523ab850ffef467ab76f/?utm_source=claude_code) — Allport, R. (2011), book chapter. Cited for: commercial speeds — fully-segregated metro 30–40 km/h, partly-segregated LRT ~20 km/h, BRT 17–20 km/h.

[11] [Methodology for calculating passenger capacity in bus rapid transit systems: Application to the TransMilenio system in Bogotá, Colombia](https://consensus.app/papers/details/91310d07a99f53dabc442a547c0f5cd3/?utm_source=claude_code) — Hidalgo, D., et al. (2013), *Research in Transportation Economics*. Cited for: TransMilenio BRT commercial speed 22–24 km/h.

[12] [Urban Densities and Transit: A Multi-dimensional Perspective](https://consensus.app/papers/details/bd2abaae8d0955788b91f71ab7a9f839/?utm_source=claude_code) — Cervero, R. & Guerra, E. (2011). Cited for: ~30 people/gross acre near stations for cost-effective light rail; ~45 for heavy rail.

[13] [Distributions of walking access to public transport in Melbourne, Australia – Evidence on acceptable and tolerable walking distances](https://consensus.app/papers/details/8b1f333556f45629ade3c0f6107822b5/?utm_source=claude_code) — Taylor, M. A. P., et al. (2024), *International Journal of Sustainable Transportation*. Cited for: AWD vs TWD framework; Burr Type XII fit to walking-access distances.

[14] [Measuring Access and Egress Distance and Catchment Area of Multiple Feeding Modes for Metro Transferring Using Survey Data](https://consensus.app/papers/details/0497db937f2d55c58b433b0efc887059/?utm_source=claude_code) — Li, X., et al. (2022), *Sustainability*. Cited for: catchment differences urban vs suburban; ~8 min average feeding time for docked bike-sharing.

[15] [On bus ridership and frequency](https://consensus.app/papers/details/b6eb84d6ecd8546ca1439a0afc6a6095/?utm_source=claude_code) — Berrebi, S. J., et al. (2021), *Transportation Research Part A*. Cited for: ridership-frequency elasticity findings — elastic between routes, inelastic within-route over time; low-frequency routes most sensitive.
