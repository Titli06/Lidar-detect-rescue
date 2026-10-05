# Project Log — LiDAR Fire-Victim Detection

> A running research journal: what I decided, what I tried, what failed, and
> why. Newest entries at the top of each section. This is deliberately rough —
> it records the *thinking*, not just the results.

**Project:** Detecting human victims in industrial-fire smoke from LiDAR point
clouds.
**Author:** Sarmili Chanda (Titli) · B.Tech Industrial Design, NIT Rourkela
**Phase:** 1 — method proof-of-concept on synthetic data
**Status (2026-10-04):** Working end-to-end pipeline + 3-way trial comparison +
figures. Ready to show for feedback.

---

## 1. The problem, stated honestly

Industrial fire, firefighters cannot see victims. The usual sensors fail:
- **Normal cameras**: blind in smoke and darkness.
- **Thermal cameras**: fail in a *specific* way — in a super-heated fire a live
  victim's skin is much cooler than the surroundings, so they show up **dark,
  not bright**, and can blend into the background ("thermal crossover"). This is
  the strongest justification for needing a different sensor.

**Key realisation (do not oversell LiDAR):** LiDAR does **not** cleanly see
through smoke either — the laser scatters off smoke particles, so returns come
back attenuated and buried in backscatter "ghost" points. The value of LiDAR is
that it captures **3D geometry that doesn't saturate the way thermal does in
high heat**, and the victim's shape is *recoverable* from the messy return with
the right processing. **That recovery is the project.** Reframed thesis:

> *The victim's 3D shape survives, in degraded form, inside a noisy LiDAR return
> even in a hot smoky room. The contribution is an ML method that recovers it.*

---

## 2. Decisions (D-xx)

**D-01 — Two-phase plan.** Phase 1 = method on synthetic data (perfect ground
truth, matched clean/smoky pairs, no hardware risk). Phase 2 = validation on the
department-lab LiDAR with real theatrical smoke + a mannequin. Rationale: the
lab unit's working state is unknown; proving the method first means that if the
hardware disappoints, Phase 1 still stands as a complete, publishable result,
and in Phase 2 any failure is clearly hardware, not method.

**D-02 — Synthetic scenes by surface-sampling, not ray-casting.** I sample
points on object surfaces rather than simulating true per-ray LiDAR returns.
Pro: self-contained, perfect labels, fast. Con: no self-occlusion modelling.
Mitigation: smoke-dropout partially stands in for missing returns. Full
occlusion is explicitly a Phase-2 (real-sensor) question.

**D-03 — Smoke as three explicit mechanisms.** attenuation dropout (Beer–Lambert
intuition: far points more likely lost), range jitter (scattering blurs
time-of-flight), and backscatter clutter (ghost points, denser near the
sensor). One knob `alpha` controls severity. Simple and inspectable on purpose;
matching real soot optics is Phase 2.

**D-04 — Three trials, increasing sophistication.** A naive baseline, a
classical denoiser, and a learned model — so the report shows a *progression*
and an ablation-style argument, not a single black box.

**D-05 — Fair baselines, not strawmen.** The classical trials get standard
pre-processing (ground-plane + wall removal) before clustering. Without it the
comparison would be dishonest (see Trial-log T-03).

**D-06 — Metric choice.** Headline = **localization error** (metres from true
victim centroid) + **hit rate** (≤ 0.5 m). Diagnostic = **victim-point recall**
(did we keep the human's points?). Recall is what exposes the core tension:
blind denoising removes noise *and* the sparse victim.

---

## 3. Trial log (T-xx) — what I ran and what happened

**T-01 — First full run (diffuse noise only, no ground removal).**
Result: Trials A and B came out **byte-identical** across all smoke levels, and
the baseline detected the victim only ~58% of the time even in *clean* air.
Diagnosis: (a) my backscatter was sparse/isolated, so DBSCAN's `min_samples`
already discarded it — classical SOR then had nothing left to remove, making A
and B identical; (b) with the floor present, the prone victim *fused into the
floor plane* under DBSCAN, so the "find a human-shaped cluster" rule failed even
with no smoke. **Lesson: the baseline was broken for an uninteresting reason
(no ground removal), which would have hidden the real effect of smoke.**

**T-02 — Added dense backscatter "puffs"; raised DBSCAN eps.**
Result: over-corrected — A and B now failed almost everywhere (hit ≈ 0,
error ≈ 3.5–4.5 m). Diagnosis: dense puffs formed false clusters that the
victim-shape gate sometimes selected, and the floor-fusion problem was still
unfixed, so the real victim often wasn't even a valid candidate.

**T-03 — Added shared ground/wall removal (D-05); kept dense puffs.**
Result: **the intended, honest story emerged.** On clean air all three work and
the *simple baseline is actually tighter* (0.05 m vs the learned model's
0.25 m) — i.e. you don't need ML when there's no smoke. As smoke thickens the
baselines collapse while the learned model stays robust. This is the result we
keep.

---

## 4. Results that matter (T-03, averaged over 12 held-out test scenes)

| smoke α | A hit% | B hit% | **C hit%** | A err(m) | B err(m) | **C err(m)** | A recall | B recall | **C recall** |
|--------:|-------:|-------:|-----------:|---------:|---------:|-------------:|---------:|---------:|-------------:|
| 0.0 | 92 | 92 | **92** | 0.06 | 0.05 | **0.25** | 0.85 | 0.84 | **0.84** |
| 0.3 | 67 | 67 | **92** | 1.19 | 1.10 | **0.26** | 0.60 | 0.60 | **0.83** |
| 0.6 | 42 | 42 | **92** | 1.20 | 1.15 | **0.40** | 0.37 | 0.37 | **0.82** |
| 0.9 | 42 | 42 | **83** | 1.69 | 1.69 | **0.36** | 0.36 | 0.36 | **0.80** |
| 1.2 | 25 | 42 | **83** | 2.18 | 2.07 | **0.33** | 0.21 | 0.35 | **0.72** |

Reading it:
- **Baselines degrade steeply with smoke** — hit rate falls to 25–42%,
  localization error climbs past 2 m, victim recall collapses.
- **The learned model is roughly flat** — it holds ~83–92% hits and ~0.25–0.40 m
  error across all smoke levels, because it learned to *keep* victim points.
- **Honest caveats:** (1) on clean air the baseline localizes *tighter* than the
  learned model; ML earns its place only under degradation. (2) Even the learned
  model's recall falls (0.84 → 0.72) at heavy smoke — attenuation genuinely
  destroys points; no method invents what the laser never received.
- **A vs B:** classical SOR helps only at the heaviest smoke (α=1.2: recall
  0.35 vs 0.21), confirming denoising matters once clutter is dense.

Learned-model feature importance (why it works): `height` 0.38, `knn_mean` 0.24,
`local_density` 0.16 — it learned victims are low to the ground, locally dense,
and not isolated the way backscatter is.

---

## 5. Known limitations (be upfront in the viva)

1. **Synthetic smoke ≠ real soot.** Particle optics, heat shimmer, and true
   per-ray dropout are approximated. → Phase 2.
2. **No self-occlusion.** Surface sampling sees all faces; a real LiDAR sees one
   side. → Phase 2.
3. **Single victim per scene, prone pose only.** Multiple/partially-buried
   victims and varied poses are future work.
4. **Centroid-level detection.** We output a location, not a full reconstructed
   mesh. Shape reconstruction is a natural extension.
5. **Classifier, not a modern point network.** RandomForest on hand-made
   features was chosen for speed and interpretability in Phase 1; a PointNet++ /
   PointPillars backbone is the obvious upgrade.

---

## 6. Next steps

- [ ] Find out the exact make/model of the lab LiDAR; confirm it powers on and
      how to pull data off it.
- [ ] Settle the data question with the professor: real smoke-chamber + mannequin
      capture, or simulation-only? (changes how results are framed)
- [ ] Swap RandomForest → a small PointNet++ and compare.
- [ ] Add shape reconstruction (not just centroid).
- [ ] Multi-victim scenes + partial burial under debris.
- [ ] Phase 2: capture a handful of real degraded scans for external validation.
