# LiDAR Fire-Victim Detection — Phase 1 (synthetic proof of concept)

Detecting human victims in industrial-fire smoke from **LiDAR point clouds**,
using AI to recover the victim's shape from a degraded return.

**Author:** Sarmili Chanda (Titli) · B.Tech Industrial Design, NIT Rourkela
(final-year capstone)

> **One-line thesis.** LiDAR does not magically see through smoke — the laser
> scatters too. But the victim's 3D shape *survives in degraded form* in the
> return, where a thermal camera would saturate in the heat. This project is the
> ML method that recovers it.

---

## What this repo shows (Phase 1)

1. A **synthetic indoor-fire scene** generator (floor, walls, a prone victim,
   debris distractors) with perfect ground-truth labels.
2. A **physically-motivated smoke model** (attenuation dropout + range jitter +
   backscatter clutter) controlled by one density knob `alpha`.
3. **Three processing trials**, compared head-to-head:
   - **A — baseline:** ground/wall removal → cluster → victim-shape gate.
   - **B — classical:** add Statistical Outlier Removal before clustering.
   - **C — learned (ours):** a per-point classifier trained to **keep victim
     points while dropping noise**, then cluster the predicted victim.
4. A **quantitative sweep** across smoke levels + **before/after figures**.

### Headline result
The learned model holds **~0.25–0.40 m** localization error and **83–92%**
hit-rate across all smoke levels, while the classical baselines degrade from
~0.05 m (clean) to **>2 m** under heavy smoke. See `figures/` and `PROJECT_LOG.md`.

Honest caveat built into the result: on *clean* air the simple baseline is
actually tighter than the learned model — ML earns its place only under smoke.

---

## Repo layout

```
lidar-fire-victim/
├── README.md            <- this file
├── LITERATURE.md        <- need analysis + 4-strand literature review + refs
├── PROJECT_LOG.md       <- research journal: decisions, trials, failures, next steps
├── run_experiments.py   <- train Trial C, run the smoke sweep, save results
├── make_figures.py      <- qualitative + quantitative figures
├── src/
│   ├── scene.py         <- synthetic labelled scene generator
│   ├── smoke.py         <- smoke degradation model (alpha)
│   ├── features.py      <- per-point geometric features + classical SOR
│   ├── trials.py        <- the three trials (A baseline / B classical / C learned)
│   └── metrics.py       <- localization error, hit-rate, victim recall
├── results/             <- results.csv / results.json (generated)
└── figures/             <- before/after + metrics-vs-smoke PNGs (generated)
```

## How to run

```bash
pip install numpy scipy scikit-learn matplotlib    # once
python3 run_experiments.py                          # ~15 s: trains, sweeps, plots
```
Outputs land in `results/` and `figures/`. Everything is seeded for
reproducibility.

## Method at a glance

- **Features per point (7):** range, height, local density, mean-kNN distance,
  kNN-distance std, local-PCA planarity, local-PCA linearity. These separate
  *backscatter* (isolated → high kNN distance) from *floor/wall* (planar) from
  the *victim* (low, compact, blobby) without needing colour or intensity.
- **Trial C classifier:** RandomForest (class-balanced). Chosen for Phase 1 for
  speed and interpretability; the obvious upgrade is a PointNet++/PointPillars
  backbone (see `PROJECT_LOG.md` → Next steps).

## Status & roadmap

Phase 1 (this repo): **done** — method validated in simulation.
Phase 2: validate on the department-lab LiDAR with real theatrical smoke + a
mannequin; swap in a point-network backbone; add shape reconstruction and
multi-victim scenes. Full list in `PROJECT_LOG.md`.

## Limitations (read before over-claiming)

Synthetic smoke ≠ real soot optics; no self-occlusion modelling; single prone
victim per scene; centroid-level output (not a full mesh). All are Phase-2 items.
