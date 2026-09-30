# PARALLAX System Architecture & Feature Reference Guide
## Updated Frontend Implementation Specification & Capabilities Manual

**Project Name:** PARALLAX — Adaptive Multi-Modal Registration Framework for Chandrayaan-2 Lunar Imagery  
**Primary Mission Workflow:** Cross-instrument lunar image correspondence and registration  
**Primary Observation Pairs:**  
- $\text{OHRC} \leftrightarrow \text{TMC-2}$ (~20× scale disparity, panchromatic high-res to stereo context)  
- $\text{TMC-2} \leftrightarrow \text{IIRS}$ (~16× scale disparity, visible stereo to hyperspectral SWIR)  
- $\text{OHRC} \leftrightarrow \text{IIRS}$ (~320× extreme scale disparity, visible ultra-high-res to hyperspectral SWIR)  
*(Same-instrument multi-temporal registration is also supported, but cross-instrument registration is the primary operational use case).*  
**Stack:** React 18, TypeScript, Tailwind CSS v4, Three.js (@react-three/fiber, @react-three/drei), GSAP, Lucide React, Vite  
**Coordinate Datum:** IAU/IAG Mean Earth/Polar Axis (ME) Reference Frame ($R = 1,737.4\text{ km}$)  

---

## 1. Architectural Guardrails & Frontend Division

### 1.1 Strict 7-Page Architecture (No Route Expansion)
The application strictly comprises **7 dedicated pages**. In accordance with core architectural rules:
- **NO new pages or routes are introduced.**
- **NO separate preprocessing page** (integrated directly into Correspondence).
- **NO separate model selection page** (integrated directly into Correspondence).
- **NO separate results or comparison page** (integrated into Correspondence & Analysis).
- **NO separate registration or uncertainty page** (integrated into Correspondence & Analysis).
- Existing visual hierarchy, typography, dark/light editorial color coding (`#111111` / `#F7F7F5`), cards, and kinetic navigation remain intact.

### 1.2 Functional Categorization of the 7 Pages
| Category | Route | Page Title | Primary Functional Role |
|---|---|---|---|
| **Discovery** | `/` | **MISSION** | Problem narrative, motivation, 10-stage workflow, and 5 architectural pillars |
| **Discovery** | `/explore` | **EXPLORE** | Lunar selenography, 3D crater targeting, and observation product discovery |
| **Discovery** | `/instruments` | **INSTRUMENTS** | Payload physics, optical bandwidths, and A/B pair configuration |
| **Operation** | `/correspondence` | **CORRESPONDENCE** | **The Central Operational Engine:** Observability gate, preprocessing, pair characterization, model router, visual alignment, and execution |
| **Evidence** | `/analysis` | **ANALYSIS** | Quantitative registration verification, adaptive transformation models, error histograms, and quality gates |
| **Demonstration** | `/simulator` | **SIMULATOR** | Controlled synthetic stress testing (labeled strictly as `SYNTHETIC / SIMULATED`) |
| **Scientific Credibility** | `/about` | **ABOUT** | Scientific motivation, peer-reviewed literature, and updated implementation maturity matrix |

---

## 2. End-to-End Global Data Flow

The operational pipeline connects input products to final verification through an 11-step backend lifecycle:

```
                  PRODUCT A  +  PRODUCT B
                             │
                             ▼
                   METADATA / GEOMETRY
                             │
                             ▼
                 [ GEOMETRIC OBSERVABILITY GATE ]
                       │                   │
                     FAIL                 PASS
                       │                   │
                  Explain Why              ▼
              (e.g., No 2D Overlap)   PREPROCESSING
                                           │ (Radiometric norm, NLM, CLAHE)
                                           ▼
                                 PAIR CHARACTERIZATION
                                           │ (Scale ratio, modality, sun angles, entropy)
                                           ▼
                                    ADAPTIVE ROUTER
                                           │
                  ┌────────────────────────┼────────────────────────┐
                  ▼                        ▼                        ▼
               Model A                  Model B                  Model C ...
           (RIFT, HOPC)             (CFOG, SIFT)          (LightGlue, LoFTR)
                  │                        │                        │
                  └────────────────────────┼────────────────────────┘
                                           ▼
                                   CONFIDENCE FILTER
                                           │
                                           ▼
                                 GEOMETRIC VERIFICATION
                                           │ (RANSAC / MSAC)
                                           ▼
                                    SPATIAL COVERAGE
                                           │ (ANMS dispersion check)
                                           ▼
                                  SUB-PIXEL REFINEMENT
                                           │ (ECC local tuning)
                                           ▼
                                   QUALITY ASSESSMENT
                                           │ (RMSE & uncertainty gates)
                       ┌───────────────────┴───────────────────┐
                       ▼                                       ▼
             CORRESPONDENCE VIEWER                      ANALYSIS RESULTS
          (4-mode visual comparison,                 (Adaptive matrix H, RMSE,
            raw/processed/registered)                  dispersion & CDF curves)
```

---

## 3. Global Shared Integrations Across All Pages

All pages share core foundational components defined in [App.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/App.tsx):

### 3.1 Global State Store (`ParallaxContext.tsx`)
- **Centralized Reactive State:** Manages active region, source/target instrument assignments, specific observation product IDs (`LunarImageProduct`), viewer comparison modes, pipeline execution status, and simulation parameters.
- **Dynamic Pair Characterization Engine (`evaluatePair`):** Calculates ground sampling distance (GSD) ratios, modality differences, illumination angle deltas, and difficulty ratings (`Easy`, `Medium`, `Hard`).
- **Backend-Driven Model Routing:** Ranks 6 candidate algorithms based on real pair physics.
- **Spatial Suppression & Sub-Pixel State:** Toggles Adaptive Non-Maximal Suppression (ANMS) and Enhanced Correlation Coefficient (ECC) subpixel local tuning.

### 3.2 Sterling Gate Kinetic Navigation (`ParallaxNavigation.tsx` / `SterlingGateKineticNavigation.tsx`)
- **GSAP-Powered Navigation Overlay:** Restrained full-viewport menu triggered via `MENU` in the global header bar.
- **Route Tracking & Telemetry Badge:** Renders active route indicator, live sensor pair badge (`OHRC × TMC-2`), and current selenographic target.
- **Global Explain Mode Toggle:** Replaces complex photogrammetric jargon with plain-English scientific explanations across all 7 pages.

### 3.3 Global Grounded Scientific AI Terminal (`ContextualAssistant.tsx`)
- **Floating Interactive Assistant:** Accessible via HUD trigger button in the bottom-right corner of all pages.
- **Session-Grounded Telemetry Sync:** Injects the active crater site, selected sensor pair, diagnosed difficulty, active correspondence engine, measured RMSE, and spatial dispersion directly into its reasoning prompt.
- **One-Click Scientific Quick Questions:** Pre-configured prompts addressing ANMS spatial dispersion, model selection rationale, the TMC-2 bridge conditions, and uncertainty quantification.
- **Data Provenance Badging:** Every response explicitly flags whether metrics reflect calibrated flight benchmarks or synthetic sandbox simulations.

### 3.4 Precision Custom Cursor & Scroll Isolation
- **`CustomCursor.tsx`:** Desktop reticle showing dynamic action prompts on hover (`TARGET FAUSTINI`, `INSPECT OHRC`, `RUN REGISTRATION`).
- **`ScrollToTop.tsx`:** Guarantees every route transition starts strictly at scroll position `(0, 0)`.
- **`GlobalFooter.tsx`:** Displays IAU lunar coordinate datums, mission readiness status, and quick site jumps.

---

## 4. Page 01 — MISSION (`/`)
**File:** [src/pages/HomePage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/HomePage.tsx)  
**Functional Role:** Discovery / Explanatory Entry Point  
**Backend Role:** None directly (primarily explanatory)

### Integrated Components:
- [HeroSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/HeroSection.tsx): Landing hero with background orbital video and authoritative typography.
- [ProblemNarrative.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/ProblemNarrative.tsx): Multi-column editorial breakdown of cross-instrument lunar imaging challenges.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **Orbital Video Hero Stage:**
   - Loop-muted orbital video (`/hero-background.mp4`) with restrained dark gradients (`#111111`).
   - Dynamic Inter typography with dual-mode descriptions adapted to the `explainMode` setting.
   - Primary action buttons: *"CORRESPONDENCE STUDIO"* (deep link to `/correspondence`) and *"EXPLORE THE MOON"* (deep link to `/explore`).
2. **"Observed Through Different Eyes" Narrative:**
   - Detailed analysis of why fixed-pipeline algorithms fail when applied to heterogeneous lunar datasets.
   - Contrasts OHRC's ultra-high spatial resolution against TMC-2's 3D stereo context and IIRS's 256-channel mineral absorption signatures.
   - Explains non-linear crater rim shadow migration under grazing polar sunlight.
3. **10-Stage Adaptive Workflow Visualization:**
   - Visual step-by-step diagram of the complete PARALLAX registration lifecycle:
     - `01 Input` (Orbital Imagery)
     - `02 Pair Formation` (Footprint Intersect)
     - `03 Physics Preprocessing` (NLM & CLAHE)
     - `04 Pair Characterization` (GSD & Modality Gap)
     - `05 Adaptive Routing` (Rank Model Bank)
     - `06 Correspondence` (Phase/Gradient Match)
     - `07 Geometric Verification` (RANSAC / MSAC)
     - `08 Spatial Coverage` (ANMS Cluster Suppression)
     - `09 Sub-Pixel Refinement` (ECC Local Tuning)
     - `10 Quality & Output` (RMSE & Uncertainty)
4. **5 Architectural Innovation Pillars:**
   - **Pillar 01: Pair-Aware Adaptive Model Selection:** Diagnoses pair difficulty and ranks matching engines dynamically.
   - **Pillar 02: TMC-2 Intermediate Scale Bridge:** Conditional two-hop progressive alignment for extreme scale pairs (`OHRC → TMC-2 → IIRS`).
   - **Pillar 03: Physics-Aware Lunar Preprocessing:** NLM de-striping, DSNU calibration, and CLAHE shadow enhancement.
   - **Pillar 04: Spatially Distributed Correspondences:** Enforces convex-hull spatial dispersion using ANMS.
   - **Pillar 05: Sub-Pixel + Uncertainty-Aware Validation:** MSAC consensus + ECC sub-pixel refinement with 1-sigma uncertainty bounds.
5. **Interactive Launchpad Strip:** Quick jump cards into the Simulator sandbox (`/simulator`), 3D Moon Explorer (`/explore`), and Instrument Lab (`/instruments`).

---

## 5. Page 02 — EXPLORE (`/explore`)
**File:** [src/pages/ExplorePage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/ExplorePage.tsx)  
**Functional Role:** Discovery / Selenography  
**Backend Role:** Product & catalogue metadata discovery

### Integrated Components:
- [MoonExplorerSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/MoonExplorerSection.tsx): Target selector bar, 3D globe viewport, and target telemetry panel.
- [MoonCanvas.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/three/MoonCanvas.tsx) & [MoonSphere.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/three/MoonSphere.tsx): WebGL 3D lunar rendering via Three.js and React Three Fiber.
- [regionsData.ts](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/data/regionsData.ts): Calibrated database of lunar landing sites and polar craters.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **Interactive Region Target Selector Bar:**
   - Fast selection buttons for 4 calibrated observation corridors:
     - **Faustini Rim** (87° 11' S, 84° 19' E — South Polar high-relief PSR boundary with steep crater walls).
     - **Boguslawsky-E** (70° 54' S, 53° 48' E — Prime high-latitude landing site corridor).
     - **Shackleton Ridge** (89° 39' S, 00° 00' W — Connecting ridge with grazing 0.8°–2.2° illumination).
     - **Tycho Peak** (43° 18' S, 11° 22' W — High-contrast Copernican central peak complex).
2. **Interactive 3D Lunar Globe Stage:**
   - 3D lunar globe with high-resolution surface textures, bump mapping, and space lighting.
   - Interactive orbit controls supporting 360° click-and-drag rotation, zoom, and orientation.
   - Dynamic corner HUD reticles displaying selenographic coordinates and rotation mode.
3. **Region-to-Observation Product Discovery Flow:**
   - Reuses existing layout to execute the required discovery chain:
     $$\text{REGION} \longrightarrow \text{AVAILABLE OBSERVATIONS} \longrightarrow \text{OHRC / TMC-2 / IIRS} \longrightarrow \text{CREATE PAIR} \rightarrow$$
   - Displays available payload tags for the targeted crater (`OHRC`, `TMC-2`, `IIRS`).
   - Action buttons: *"VIEW SENSORS"* (`/instruments`) and *"CREATE PAIR →"* (`/correspondence`).
4. **Active Target Telemetry Dossier:**
   - Displays exact selenographic latitude/longitude, elevation relief datum (e.g., `-1,420 m to +850 m`), surface roughness (Hurst exponent 0.62), and solar lighting condition.
   - **Automated Registration Difficulty Diagnosis:** Classifies site difficulty (`HIGH (LOW SUN)` vs `MODERATE`) with matching strategy guidance.
5. **Selenodetic Ground Control & Reference Catalogue:**
   - Technical benchmark table mapping Target Sites, IAU Coordinates, Solar Elevation Angles, Sensor Gaps, and Primary Recommended Matching Strategies.

---

## 6. Page 03 — INSTRUMENTS (`/instruments`)
**File:** [src/pages/InstrumentsPage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/InstrumentsPage.tsx)  
**Functional Role:** Discovery / Payload Lab  
**Backend Role:** Instrument specifications & A/B configuration state

### Integrated Components:
- [InstrumentLabSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/InstrumentLabSection.tsx): Interactive payload cards and deep-dive optical dossiers.
- [instrumentsData.ts](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/data/instrumentsData.ts): Official ISRO Chandrayaan-2 camera hardware specifications.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **Observation Physics Comparison Matrix:**
   - Technical table detailing:
     - **OHRC:** ~0.25–0.32 m/px GSD, panchromatic, 3.0 km swath, 1250 mm focal length, 12-bit TDI-CCD linear array. Challenge: extreme scale aliasing.
     - **TMC-2:** ~5.0 m/px GSD, panchromatic visible stereo (Fore +26°, Nadir 0°, Aft -26°), 20 km swath, 10-bit linear CCD. Role: 3D DEMs and intermediate scale bridge.
     - **IIRS:** ~80 m/px GSD, 256 contiguous hyperspectral bands (0.8–5.0 µm), 20 km swath, HgCdTe focal plane array. Challenge: 320:1 scale disparity and radiometric contrast inversion.
2. **Interactive Payload Profile Selector Cards:**
   - Clickable cards for OHRC, TMC-2, and IIRS highlighting GSD badges, mission purposes, and spectral passbands.
3. **Deep-Dive Instrument Technical Dossier:**
   - Hardware specifications: detector architectures, radiometric dynamic ranges (10-bit vs 12-bit), focal lengths, swath dimensions, and calibration archive IDs.
   - Detailed analysis of the specific registration challenges each sensor introduces into cross-instrument pairing.
4. **Interactive Pair Assignment Controls (`A/B Selection`):**
   - Clickable buttons: *"SET AS SOURCE (A)"* and *"SET AS TARGET (B)"*.
   - **Crucial Rule:** Directly updates the global `ParallaxContext` store (`sourceInstrument`, `targetInstrument`).
5. **Real-Time Pair Preview Box (Integrated Inside Existing Page):**
   - **GSD Gap Readout:** Displays scale disparity (`~20×` for OHRC ↔ TMC-2, `~16×` for TMC-2 ↔ IIRS, or `~320×` for OHRC ↔ IIRS).
   - **Modality Gap Readout:** Displays spectral transition (e.g., `Panchromatic → Hyperspectral`).
   - **Pair Difficulty Badge:** Dynamically evaluates and displays `EASY`, `MEDIUM`, or `HARD` with scientific rationale.
   - **TMC-2 Intermediate Scale Bridge Display:** For extreme-scale pairs (`OHRC → TMC-2 → IIRS`), explicitly surfaces the bridge as a *candidate / proposed strategy* rather than presenting it as proven for every pair.
   - Direct 1-click CTA: *"OPEN IN STUDIO →"*.

---

## 7. Page 04 — CORRESPONDENCE (`/correspondence`)
**File:** [src/pages/CorrespondencePage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/CorrespondencePage.tsx)  
**Functional Role:** The Central Operational Engine  
**Backend Role:** Full registration workflow trigger, observability gating, preprocessing, model routing, and inlier/outlier verification

### Integrated Components:
- [CorrespondenceStudioSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/CorrespondenceStudioSection.tsx): Orchestrates the 4 horizontal studio bands.
- [PairSelectionControlArea.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/PairSelectionControlArea.tsx): 3-column top control console with observability gate.
- [PairAnalysisPanel.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/PairAnalysisPanel.tsx): Difficulty characterization and scale bridge status.
- [AdaptiveModelRouter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/AdaptiveModelRouter.tsx): Ranked model bank with manual testing triggers.
- [DualImageComparator.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/DualImageComparator.tsx) & [MatchCanvas.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/MatchCanvas.tsx): Multi-modal visual alignment viewport with viewer state modes.
- [FilterToggle.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/FilterToggle.tsx): Match filters, ANMS dispersion toggle, and sub-pixel refinement switches.
- [PipelineStepper.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/correspondence/PipelineStepper.tsx): Live 10-stage backend pipeline status stepper.
- [correspondenceService.ts](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/services/correspondenceService.ts): Asynchronous backend execution interface.

### Page Features & Capabilities:
1. **Actual Product Selection (3-Column Console):**
   - The UI selects **actual backend observation products** (e.g., `CH2_OHR_NCP_20201115T083210`), not merely generic sensor names.
   - **Source A & Target B Cards:** Display actual product ID, acquisition timestamp, GSD (`0.25 m/px`), solar elevation (`14.5°`), solar azimuth (`72.0°`), dimensions, thumbnail preview, and full metadata.
   - Quick `Swap Instruments (A ↔ B)` button and `Reset` button.
2. **Observability / Geographic Overlap Gate (Pre-Matching Check):**
   - Integrated directly inside the existing control area before expensive matching begins:
     - **If Overlap Exists:** Displays `GEOMETRIC OBSERVABILITY: ✓ Geographic overlap, ✓ Valid pixels, ✓ Observable area, ✓ Registration candidate`.
     - **If No Overlap Exists:** Displays `REGISTRATION BLOCKED: No valid geographic overlap` (e.g., test pair `P0001` where OHRC and TMC-2 do not share 2D ground footprint).
3. **Compact Preprocessing Controls:**
   - In-place compact controls (no separate page):
     - Lifecycle: $\text{Raw / Calibrated} \to \text{Radiometric Normalization} \to \text{Noise Stabilization} \to \text{CLAHE Enhancement} \to \text{Multi-Scale Representation} \to \text{Matcher-Ready}$.
     - User controls: Preprocessing `AUTO`, `CLAHE: ON/OFF`, radiometric normalization toggle.
4. **Dynamic Pair Characterization:**
   - Calculates dynamically:
     - *Scale:* GSD A, GSD B, scale ratio ($20.0:1$ up to $320.0:1$).
     - *Modality:* Panchromatic, visible stereo, or hyperspectral SWIR.
     - *Illumination:* Solar elevation angles and delta.
     - *Image Characteristics:* Texture strength, gradient similarity, edge density, entropy, and valid pixel ratio.
   - Output: `PAIR DIFFICULTY: EASY / MEDIUM / HARD` with a concise scientific reason.
5. **Adaptive Model Bank (6 Candidate Engines):**
   - Models evaluated: **RIFT**, **HOPC**, **CFOG**, **SuperPoint + LightGlue**, **LoFTR**, and **SIFT baseline**.
   - **Critical Rule:** Suitability scores (e.g., `96%`) and rankings are **backend-driven**, not hardcoded.
   - Displays model name, category, rank, score, execution runtime, and selection rationale.
   - **Manual Testing Trigger:** Users can click *"TEST MODEL"* to run an individual candidate against the active pair.
6. **TMC-2 Intermediate Scale Bridge:**
   - For extreme-scale pairs (`OHRC ↔ IIRS` at 320:1):
     $$\text{STEP 1: OHRC} \to \text{TMC-2} \quad\longrightarrow\quad \text{STEP 2: TMC-2} \to \text{IIRS} \quad\longrightarrow\quad \text{STEP 3: Composite Transformation}$$
   - Clearly documented as a candidate/proposed strategy requiring empirical validation.
7. **Pipeline Execution Trigger:**
   - *"RUN REGISTRATION PIPELINE"* acts as the actual backend trigger sending `source_product`, `target_product`, `selected_model`, `bridge_enabled`, `preprocessing_options`, `ANMS`, and `subpixel_refinement`.
8. **Live Pipeline Stepper:**
   - Displays real backend execution state across all 10 stages (`INPUT`, `PAIR FORMATION`, `PREPROCESSING`, `CHARACTERIZATION`, `ROUTING`, `CORRESPONDENCE`, `GEOMETRIC VERIFY`, `SPATIAL COVERAGE`, `SUB-PIXEL`, `QUALITY`).
9. **Advanced Image Comparison with Viewer States:**
   - **4 Comparison Modes:** Side-by-Side (with vectors), Split Slider, Onion Skin, and Checkerboard.
   - **Viewer State Selector (Integrated in place):**
     $$\text{VIEW: } \text{Original (Raw)} \;\longrightarrow\; \text{Preprocessed} \;\longrightarrow\; \text{Registered}$$
   - Allows full verification of raw inputs, contrast-enhanced frames, and final aligned mosaics.
10. **Match Inspection & Spatial Coverage Metrics:**
    - Counters for `RAW MATCHES`, `FILTERED`, `INLIERS`, and `OUTLIERS`.
    - Interactive vector inspection exposing: `(x, y) → (x', y')`, reprojection residual, and confidence score.
    - **Spatial Coverage Readouts:** Displays Source Coverage, Target Coverage, and Uniformity, reinforcing that *more matches do not automatically guarantee better registration; spatial distribution matters*.
11. **Sub-Pixel Refinement Readout:**
    - ECC refinement displays real before/after values: `BEFORE RMSE: X.XX px`, `AFTER RMSE: X.XX px`, `GAIN: -X.XX px` (displayed only after actual refinement execution).

---

## 8. Page 05 — ANALYSIS (`/analysis`)
**File:** [src/pages/AnalysisPage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/AnalysisPage.tsx)  
**Functional Role:** Evidence / Quantitative Evaluation  
**Backend Role:** Consumes completed registration results; renders transformation models and uncertainty metrics

### Integrated Components:
- [AnalysisSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/AnalysisSection.tsx).
- [MetricCards.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/analysis/MetricCards.tsx): Primary telemetry cards.
- [HomographyDisplay.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/analysis/HomographyDisplay.tsx): Adaptive transformation model viewer.
- [ErrorPlot.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/analysis/ErrorPlot.tsx): SVG error histogram and CDF curves.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **Backend-Driven Quantitative Metrics (No Fake Hardcoded Values):**
   - Replaces static placeholder values with dynamic results returned by the backend:
     - **Correspondence:** Raw matches, filtered matches, confirmed inliers, inlier ratio (%).
     - **Geometry:** RMSE (px), mean error, median error, maximum error.
     - **Spatial Distribution:** Source coverage (%), target coverage (%), uniformity score.
     - **Refinement:** Before RMSE, after RMSE, improvement delta.
     - **Confidence & Uncertainty:** Covariance uncertainty bounds (1-sigma ellipse).
2. **Adaptive Transformation Model Viewer:**
   - **Crucial Rule:** Does NOT force every result into a homography matrix.
   - If backend returns a **Planar Homography**, renders the 3×3 matrix $H$ with affine parameter decomposition (scale, rotation $\theta$, translation $T_x, T_y$, shear, perspective tilt).
   - If backend returns an **Affine**, **Local / Piecewise**, or **Thin-Plate Spline** transformation, renders the appropriate geometric representation.
3. **Reprojection Error Residual Histogram & CDF Curves:**
   - SVG histogram showing inlier error distributions against the MSAC consensus cutoff.
   - Cumulative Distribution Function (CDF) curve verifying what percentage of inliers achieve sub-pixel accuracy.
   - Lowe distance ratio distribution separating valid inliers from ambiguous candidates.
4. **Planar Homography Validity & Outlier Audit Editorial Section:**
   - Mathematical justification of projective approximations at 100 km lunar orbit altitude ($<2\%$ relief ratio).
5. **Simulator Sandbox Launchpad:** Direct CTA button transitioning into `/simulator`.

---

## 9. Page 06 — SIMULATOR (`/simulator`)
**File:** [src/pages/SimulatorPage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/SimulatorPage.tsx)  
**Functional Role:** Demonstration / Controlled Stress Testing  
**Backend Role:** Client-side / synthetic sandbox engine

### Integrated Components:
- [SimulatorSection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/SimulatorSection.tsx).
- [LunarSimulator.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/simulator/LunarSimulator.tsx): Interactive parameter sliders, procedural canvas, and stress-test benchmark table.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **Mandatory Provenance Distinction (`SYNTHETIC / SIMULATED`):**
   - The entire page and its readouts are prominently badged as **`SYNTHETIC / SIMULATED DATA`**.
   - Ensures simulated sandbox tests are never conflated with actual Chandrayaan-2 flight measurements.
2. **Interactive Stress-Testing Parameter Sliders:**
   - **Solar Elevation Angle ($0.5^\circ$ to $45.0^\circ$):** Simulates grazing polar sunlight and extreme crater rim shadow lengthening.
   - **Sun Azimuth Angle ($0^\circ$ to $360^\circ$):** Rotates the lighting vector to test shadow migration across crater walls.
   - **Spatial Scale Disparity Ratio ($1:1$ to $320:1$):** Simulates resolution disparities up to the extreme OHRC vs IIRS gap.
   - **Sensor Noise Sigma ($\sigma = 0.0$ to $15.0$):** Injects synthetic Gaussian noise and DSNU detector striping.
   - **CLAHE Clip Limit ($1.0$ to $8.0$):** Modulates contrast equalization to test shadow detail recovery.
   - **Shadow Mask Threshold ($10$ to $100\text{ DN}$):** Adjusts radiometric floor for classifying permanently shadowed crater basins.
3. **Instant Preset Test Scenarios:**
   - 1-click test configurations:
     - *"Shackleton Polar Rim"* ($1.5^\circ$ grazing sun, high relief).
     - *"Faustini Deep Shadow"* ($0.8^\circ$ sun, severe shadow, high noise).
     - *"Mare Tranquillitatis Equator"* ($35^\circ$ nominal sun, high contrast).
     - *"Extreme Scale Disparity"* ($320:1$ scale ratio, tests bridge triggering).
4. **Live Procedural Simulation Canvas:**
   - Real-time 2D canvas displaying synthetic lunar crater terrain, dynamic cast shadows, detector noise patterns, and detected keypoint stability.
5. **Real-Time Algorithm Stress Test Benchmark Table:**
   - Evaluates all 6 models against active slider parameters, predicting Inlier Ratios, RMSE, and Failure Risk levels (`Low`, `Moderate`, `High`, `Critical`). Demonstrates where SIFT fails and where RIFT/LoFTR excel.
6. **Methodology Launchpad:** Direct CTA button transitioning into `/about`.

---

## 10. Page 07 — ABOUT (`/about`)
**File:** [src/pages/AboutPage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/AboutPage.tsx)  
**Functional Role:** Scientific Credibility / Provenance  
**Backend Role:** Scientific documentation, literature references, and engineering audit

### Integrated Components:
- [MissionStorySection.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/sections/MissionStorySection.tsx): Narrative on the cross-instrument challenge and open science architecture.
- [AboutPage.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/pages/AboutPage.tsx): Updated maturity matrix, literature citations, and payload provenance table.
- [GlobalFooter.tsx](file:///c:/Users/graj6/Downloads/New%20folder%20%2813%29/src/components/common/GlobalFooter.tsx).

### Page Features & Capabilities:
1. **The Cross-Instrument Challenge Narrative:**
   - Details why subpixel co-registration across OHRC, TMC-2, and IIRS is essential for safe hazard avoidance and volatile water ice prospecting.
2. **Updated Implementation Maturity Matrix:**
   - Replaces older binary structures with the required 3-tier credibility framework:
     - **`IMPLEMENTED` (Code exists and executes):**
       - Pair Characterization & Difficulty Heuristic (GSD, modality, sun angles, entropy).
       - Radiometric Preprocessing (NLM noise stabilization & CLAHE contrast tuning).
       - SIFT + Ratio Test + RANSAC geometric verification.
       - Adaptive Non-Maximal Suppression (ANMS) spatial dispersion logic.
       - Sub-Pixel Refinement (ECC Gauss-Newton local patch optimization).
       - Quantitative Evaluation Gauges & Error Residual Histograms.
     - **`VALIDATED` (Actual test / benchmark evidence exists):**
       - SIFT + ANMS on Chandrayaan-2 synthetic & calibrated highland pairs.
       - Multi-scale Gaussian octave blur pyramid for moderate scale disparities ($<20:1$).
       - Planar homography validity at 100 km orbit altitude.
     - **`PROPOSED / UNDER VALIDATION` (Concept implemented, stronger scientific validation remains):**
       - **RIFT:** Phase congruency for extreme polar shadow shifts (Li et al., IEEE TIP 2020).
       - **HOPC:** Dense structural alignment for optical-to-hyperspectral pairs (Ye et al., PE&RS 2014).
       - **CFOG:** Fast 3D gradient matching for wide-swath context (Ye et al., IEEE TGRS 2019).
       - **SuperPoint + LightGlue:** Self-supervised keypoints with graph neural networks (Lindenberger et al., ICCV 2023).
       - **LoFTR:** Detector-free dense feature transformers for low-texture crater floors (Sun et al., CVPR 2021).
       - **TMC-2 Intermediate Scale Bridge:** Two-hop progressive transitive registration ($H_{\text{composite}} = H_{B \to C} \cdot H_{A \to B}$) for extreme 320:1 scale gaps.
3. **Formal Peer-Reviewed Literature Citations:**
   - Complete bibliographic citations of foundational papers with specific relevance annotations.
4. **ISRO Chandrayaan-2 Payload Provenance Table:**
   - Official hardware specifications, detector dimensions, and mission roles for OHRC, TMC-2, and IIRS.
5. **Return Launchpads:** Quick CTAs returning to the Correspondence Studio (`/correspondence`) or 3D Explorer (`/explore`).

---

## 11. Quick Reference: Page-by-Page Integration Matrix

| Page Route | Page Name | Primary Integrated Modules | Key Unique Capabilities |
|---|---|---|---|
| `/` | **MISSION** | `HeroSection`, `ProblemNarrative`, 10-Step Flow | Orbital video hero, 10-stage flow diagram, 5 architectural pillars |
| `/explore` | **EXPLORE** | `MoonExplorerSection`, `MoonCanvas` (Three.js), `regionsData` | Interactive 3D lunar globe, 4 crater sites, region-to-product discovery flow |
| `/instruments` | **INSTRUMENTS** | `InstrumentLabSection`, `instrumentsData` | Sensor physics table, deep-dive optical dossiers, `Set Source/Target` triggers, pair difficulty preview |
| `/correspondence` | **CORRESPONDENCE** | `PairSelectionControlArea`, `PairAnalysisPanel`, `AdaptiveModelRouter`, `DualImageComparator`, `PipelineStepper` | Actual product selection, **Observability Gate**, compact preprocessing (`AUTO`/`CLAHE`), backend model router, 4 comparison modes + viewer states (`Raw`/`Processed`/`Registered`), spatial coverage & subpixel readouts |
| `/analysis` | **ANALYSIS** | `MetricCards`, `HomographyDisplay`, `ErrorPlot` | Backend-driven metrics (RMSE, inliers, spatial dispersion, uncertainty), **adaptive transformation models** (Homography, Affine, Piecewise), error histogram & CDF curve |
| `/simulator` | **SIMULATOR** | `LunarSimulator` | Labeled strictly as **`SYNTHETIC / SIMULATED`**, 6 stress-testing sliders, procedural lunar canvas, real-time algorithm benchmark table |
| `/about` | **ABOUT** | `MissionStorySection`, Maturity Matrix, Citations | **Updated 3-tier maturity matrix** (`IMPLEMENTED`, `VALIDATED`, `PROPOSED / UNDER VALIDATION`), peer-reviewed bibliography, ISRO mission provenance |
