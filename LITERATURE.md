# Literature Review & Need Analysis

**Project:** AI-based detection of fire victims from LiDAR point clouds in smoke.
**Scope of this document:** establish the real need, survey what already exists
(published + market), and locate the genuine gap this capstone occupies.

---

## 1. The real need

Firefighters routinely cannot locate victims inside a fire because every
*passive* sensing route breaks down:

- **Visible cameras** are defeated by smoke and darkness.
- **Thermal imaging cameras (TICs)** — the current standard tool — fail in a
  specific, well-documented way in a developed fire. A living victim's skin is
  far cooler than the surrounding flames, so instead of appearing "white hot"
  they appear **dark or grey**, and a deceased victim can become a passive
  emitter that blends into the hot background. This is the *thermal crossover*
  problem: when ambient and target temperatures converge, the victim's contrast
  against the scene disappears. (Fire-service sources: Firehouse, Fire Apparatus
  Magazine; wildfire-robotics review in *EMST*, 2026.)

This is the core justification for a **geometry-based** sensor: LiDAR measures
*shape and distance*, which do not saturate the way a heat image does when the
whole room is hot.

**Important honest caveat.** LiDAR is **not** a magic see-through sensor. Its
laser is scattered and attenuated by smoke particles just as light is, and
backscatter from the smoke produces false returns that grow with range and
density (USPTO 11,119,212; FIReStereo sensor comparison, 2024). In controlled
smoke tests, LiDAR degrades significantly while longer-wavelength radar passes
through (Evaluation of Navigation Sensors in Fire Smoke; "LiDAR Teach, Radar
Repeat", arXiv). **So the value proposition is not "LiDAR sees through smoke" —
it is "LiDAR retains recoverable 3D structure where thermal saturates, and the
victim can be recovered from the degraded return with the right processing."**
That processing is the contribution of this project.

---

## 2. What already exists — four research strands

The topic sits at the intersection of four bodies of work. Each is strong in one
respect and missing exactly what this project needs.

### Strand 1 — Human/object detection in point clouds (mature, clean data)
3D detection of people is well-developed for autonomous driving. Workhorses:
- **PointPillars** (Lang et al., 2019) — encodes the cloud into vertical pillars
  processed as 2D convolutions; fast, strong on the KITTI car/pedestrian/cyclist
  benchmark.
- **PointNet / PointNet++** — learn directly on raw point geometry; used to
  detect pedestrians from LiDAR geometry alone (Lorente et al., 2021).
- Surveys confirm the persistent weak spot: sparse, uneven point density causes
  missed detections and false positives, *especially for pedestrians*
  (deep-learning 3D detection survey, *Sensors*, 2022; RAK-Pillars, 2025).

**Gap for us:** these assume dense, clean, upright pedestrians at street scale —
not a prone victim, partially occluded, in soot, at indoor range.

### Strand 2 — Adverse-weather point-cloud denoising (mature, wrong domain)
The closest cousin. A clear lineage of models that strip weather noise from
LiDAR:
- **WeatherNet** (Heinzler et al., 2020) — first CNN for LiDAR de-noising.
- **4DenoiseNet** (Seppänen et al., 2022) — first to use spatial *and* temporal
  (multi-frame) information.
- **AdverseNet** (2025) — one network for rain, snow and fog.
- Surveys/benchmarks catalogue the field and note remaining gaps (*Signal, Image
  and Video Processing* survey, 2025; "Benchmark for LiDAR in fog", Bijelic
  2018).

**Gap for us:** almost all of it targets **rain/fog/snow for self-driving cars**,
and the objective is to *clean the road scene* — not to **preserve and recover a
human target**. Combustion smoke (soot) differs optically from the water-droplet
fog these models train on, and "keep the victim" is a different loss than "remove
the weather."

### Strand 3 — See-through-smoke LiDAR (the frontier, exotic hardware)
Genuine reconstruction through dense smoke exists, using advanced detectors:
- **Single-photon / TCSPC LiDAR** reconstructs depth of moving objects through
  heavy obscurant (~5 attenuation lengths) at >100 m (Tobin/Buller group,
  *Scientific Reports*, 2021; real-time plug-and-play denoisers, *Nature Comms*,
  2019; 1 km imaging, *Optica*, 2025).
- **Gm-APD array LiDAR** reconstructs targets through smoke at very low
  signal-to-background ratios (*Optics & Lasers in Eng.*, 2022/2025).

**Gap for us:** this needs SPAD / superconducting-nanowire / Gm-APD hardware —
specialist and lab-bound. We cite it to prove the task is *physically possible*;
the open problem is doing a usable version on **commodity LiDAR + software**.

### Strand 4 — LiDAR search-and-rescue robotics (applied, LiDAR ≠ victim ID)
Many rescue robots carry LiDAR into disasters:
- LiDAR on rescue vehicles maps collapsed interiors and helps locate trapped
  people before responders enter (S&R robot design, 2024; crisis-response AI
  review).
- In integrated stacks, **LiDAR does SLAM/navigation while a thermal/vision
  camera does the victim sensing** (fire-victim rescue method, *Expert Systems
  with Applications*, 2023).

**Gap for us:** LiDAR is used to *drive and map*, not to *identify the victim*.
Asking the LiDAR point cloud itself to find the victim in smoke is the open space.

---

## 3. What exists in the market

- **Quadruped fire-recon robots** — e.g. DEEP Robotics **X30** carries a
  dual-spectrum camera + 3D LiDAR to build a real-time interior map and track the
  fire; 2025 drills included smoke recon and victim search in high-rise and
  collapse scenarios (DEEP Robotics press, 2026).
- **Fire-service TICs** — e.g. Seek Thermal FirePRO, with "mixed-gain" tricks to
  cope with hot scenes — but bounded by thermal crossover (§1).

**Same pattern as Strand 4:** in every shipping stack, **LiDAR draws the map and
a camera finds the person.** Recovering the victim from the *LiDAR data itself*
in smoke on commodity hardware is not a solved, productised capability.

---

## 4. The gap this capstone occupies

Putting the strands together, the white space, biggest first:

1. **The empty middle.** Strand 1 finds humans but in clean data; Strand 2
   cleans degraded data but for driving and to *remove* noise, not preserve
   humans; Strand 3 sees through smoke but needs exotic detectors; Strand 4 uses
   LiDAR only to navigate. **Victim recovery from degraded, smoke-filled LiDAR on
   commodity hardware sits in the middle of all four and is largely unoccupied.**
2. **No dataset.** There is essentially no public, labelled dataset of humans in
   fire/smoke seen by LiDAR; everything mature is driving data in rain/snow/fog.
   This is the biggest obstacle *and* a publishable contribution if even a small
   (simulated or smoke-chamber) dataset is built.
3. **Non-canonical target geometry.** Fire victims are prone, curled, or
   partially buried, close to the sensor — not upright pedestrians at 20 m.
   Detectors tuned for street-scale pedestrians are not tuned for this.

**This project's claim:** adapt point-cloud denoising/detection so that it
*preserves and recovers the human* under smoke degradation, validated first in
simulation (Phase 1) and then on real lab LiDAR + smoke (Phase 2).

---

## 5. Reference list (starter — expand as you read)

> Full bibliographic details to be completed during reading; grouped by strand.

**Need / sensing in fire**
- Firehouse — "Identifying victims with a TIC"; "Common failures of TIC use."
- Fire Apparatus Magazine — "Thermal Imaging Limitations."
- *EMST* (2026) — review of electronic systems for wildfire detection (thermal
  crossover; navigation-sensor trade-offs).
- FIReStereo (2024) — sensor comparison under smoke (visual/LiDAR vs LWIR).
- USPTO 11,119,212 — reducing DVE effect on LiDAR return (backscatter physics).

**Strand 1 — point-cloud human detection**
- Lang et al. (2019), *PointPillars*, CVPR.
- Qi et al., *PointNet / PointNet++*.
- Lorente et al. (2021), pedestrian detection in 3D point clouds (PointNet++).
- *Sensors* (2022) — survey of deep-learning LiDAR 3D detection.

**Strand 2 — adverse-weather denoising**
- Heinzler et al. (2020), *WeatherNet* (CNN LiDAR de-noising), IEEE RA-L.
- Seppänen et al. (2022), *4DenoiseNet*, IEEE RA-L.
- AdverseNet (2025); point-cloud-under-adverse-weather survey (*SIViP*, 2025).
- Bijelic et al. (2018), "A benchmark for LiDAR sensors in fog."

**Strand 3 — see-through-smoke LiDAR**
- Tobin et al. / Buller group (2021), real-time 3D imaging through obscurant,
  *Scientific Reports*.
- Real-time reconstruction with plug-and-play denoisers (2019), *Nature Comms*.
- McCarthy et al. (2025), 1 km single-photon imaging, *Optica*.
- Gm-APD depth imaging through smoke (2022/2025), *Optics & Lasers in Eng.*

**Strand 4 — SAR robotics / market**
- Search-and-rescue robot design based on LiDAR (2024).
- Fire-victim rescue method (2023), *Expert Systems with Applications*.
- DEEP Robotics X30 firefighting deployments (press, 2026).
