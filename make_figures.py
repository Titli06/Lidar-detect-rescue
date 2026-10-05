"""
make_figures.py
---------------
Qualitative + quantitative figures for the demo.

Qualitative : one example scene shown as clean / smoky / and each trial's
              recovered victim (the "before vs after" money shot).
Quantitative: localization error and victim-recall vs smoke density.
"""

import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from scene import make_scene, L_STRUCTURE, L_VICTIM, L_DEBRIS, L_NOISE
from smoke import apply_smoke
from trials import trial_a_baseline, trial_b_classical

FIG = os.path.join(os.path.dirname(__file__), "figures")
RESULTS = os.path.join(os.path.dirname(__file__), "results")

C = {L_STRUCTURE: "#c7ccd1", L_VICTIM: "#d7263d",
     L_DEBRIS: "#8d99ae", L_NOISE: "#f4a259"}


def _scatter(ax, pts, labels, title, true_centroid=None, pred_centroid=None):
    for lab, col in C.items():
        m = labels == lab
        if m.any():
            name = {L_STRUCTURE: "structure", L_VICTIM: "victim",
                    L_DEBRIS: "debris", L_NOISE: "smoke noise"}[lab]
            ax.scatter(pts[m, 0], pts[m, 1], pts[m, 2], s=2, c=col,
                       label=name, depthshade=False)
    if true_centroid is not None:
        ax.scatter(*true_centroid, s=120, marker="*", c="#1b998b",
                   edgecolors="k", label="true victim", depthshade=False)
    if pred_centroid is not None:
        ax.scatter(*pred_centroid, s=120, marker="X", c="#2e86ab",
                   edgecolors="k", label="predicted", depthshade=False)
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("x (m)"); ax.set_ylabel("y (m)")
    ax.set_zlim(0, 2.2); ax.view_init(elev=38, azim=-60)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])


def qualitative_figure(model, seed=2003, alpha=0.9):
    pts, lab, meta = make_scene(seed=seed)
    rng = np.random.default_rng(123)
    dp, dl = apply_smoke(pts, lab, alpha, rng=rng, room=meta["room"])
    tc = meta["victim_centroid"]

    cA, mA = trial_a_baseline(dp)
    cB, mB = trial_b_classical(dp)
    cC, mC = model.predict(dp)

    fig = plt.figure(figsize=(16, 9))
    specs = [
        (pts, lab, "1. Clean scene (ground truth)", None),
        (dp, dl, f"2. Degraded by smoke (alpha={alpha})", None),
        (dp, _as_pred(dp, mA), "3. Trial A - baseline (raw cluster)", cA),
        (dp, _as_pred(dp, mB), "4. Trial B - classical SOR", cB),
        (dp, _as_pred(dp, mC), "5. Trial C - learned (ours)", cC),
    ]
    for i, (P, La, title, pc) in enumerate(specs, 1):
        ax = fig.add_subplot(2, 3, i, projection="3d")
        _scatter(ax, P, La, title, true_centroid=tc, pred_centroid=pc)
        if i == 1:
            ax.legend(loc="upper left", fontsize=7, markerscale=2)
    # summary panel
    ax = fig.add_subplot(2, 3, 6); ax.axis("off")
    def err(c): return "miss" if c is None else f"{np.linalg.norm(c-tc):.2f} m"
    txt = ("Localization error (lower = better)\n\n"
           f"  Trial A  (baseline)   : {err(cA)}\n"
           f"  Trial B  (classical)  : {err(cB)}\n"
           f"  Trial C  (learned)    : {err(cC)}\n\n"
           f"Scene: victim among {int((lab==L_DEBRIS).sum()>0) and 'debris + '}"
           f"walls\nSmoke alpha = {alpha}  "
           f"(victim pts kept: {int((dl==L_VICTIM).sum())}/"
           f"{int((lab==L_VICTIM).sum())})")
    ax.text(0.02, 0.95, txt, va="top", family="monospace", fontsize=11)
    fig.suptitle("LiDAR fire-victim detection - Phase 1 (synthetic) "
                 "before vs after", fontsize=14, y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(FIG, "qualitative_before_after.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"      wrote {path}")


def _as_pred(points, mask):
    """Label array for plotting: predicted victim red, rest grey."""
    out = np.full(len(points), L_STRUCTURE)
    out[mask] = L_VICTIM
    return out


def quantitative_figures():
    with open(os.path.join(RESULTS, "results.json")) as f:
        table = json.load(f)
    alphas = sorted({float(a) for t in table for a in table[t]})
    styles = {"A_baseline": ("#8d99ae", "o", "Trial A - baseline"),
              "B_classical": ("#f4a259", "s", "Trial B - classical SOR"),
              "C_learned": ("#d7263d", "^", "Trial C - learned (ours)")}

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for t, (col, mk, lbl) in styles.items():
        le = [table[t][str(a) if str(a) in table[t] else f"{a}"]["loc_err"]
              if _get(table[t], a) else np.nan for a in alphas]
        le = [_get(table[t], a)["loc_err"] for a in alphas]
        rc = [_get(table[t], a)["vic_recall"] for a in alphas]
        axes[0].plot(alphas, le, marker=mk, color=col, label=lbl, lw=2)
        axes[1].plot(alphas, rc, marker=mk, color=col, label=lbl, lw=2)
    axes[0].axhline(0.5, ls="--", c="gray", lw=1, label="hit threshold (0.5 m)")
    axes[0].set_title("Localization error vs smoke density")
    axes[0].set_xlabel("smoke density  alpha"); axes[0].set_ylabel("mean error (m)")
    axes[0].legend(fontsize=8)
    axes[1].set_title("Victim-point recall vs smoke density")
    axes[1].set_xlabel("smoke density  alpha")
    axes[1].set_ylabel("fraction of victim points recovered")
    axes[1].set_ylim(0, 1); axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(FIG, "metrics_vs_smoke.png")
    fig.savefig(path, dpi=130); plt.close(fig)
    print(f"      wrote {path}")


def _get(d, a):
    for key in (str(a), f"{a:.1f}", f"{int(a)}" if a == int(a) else None):
        if key is not None and key in d:
            return d[key]
    return None


def main(model):
    print("      generating figures ...")
    # a deliberately HARD case: heavy smoke where the heuristics lock onto the
    # wrong object but the learned model still finds the victim.
    qualitative_figure(model, seed=2010, alpha=1.2)
    quantitative_figures()


if __name__ == "__main__":
    # allow standalone figure regen using a freshly trained model
    from run_experiments import train_learned_model
    main(train_learned_model())
