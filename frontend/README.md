# PARALLAX Frontend

High-fidelity planetary science web observatory and sub-pixel cross-sensor image co-registration interface for ISRO Chandrayaan-2 datasets (OHRC, TMC-2, IIRS).

## Architecture

- **Framework**: React 18, TypeScript, Vite
- **Styling**: TailwindCSS & Vanilla CSS design system
- **Routing**: React Router DOM (7 Dedicated Editorial Page Modules)
- **Kinetic Animations**: GSAP, Lucide React icons, Scramble text effects
- **State & Telemetry**: `ParallaxContext` with unified reactive pipeline orchestration

## Directory Structure

```
frontend/
├── public/                 # Static lunar photography assets & benchmarks
├── src/
│   ├── components/         # Reusable scientific UI components
│   │   ├── analysis/       # Homography & residual distribution displays
│   │   ├── assistant/      # Contextual telemetry AI assistant
│   │   ├── common/         # Kinetic badges, counters, and footer
│   │   ├── correspondence/ # Dual comparator, adaptive router, pipeline stepper
│   │   ├── simulator/      # Physical environmental stress simulator
│   │   └── ui/             # Sterling Gate kinetic navigation & reticles
│   ├── data/               # Planetary observation catalogues & benchmark models
│   ├── pages/              # 7 dedicated scientific pages
│   ├── sections/           # Section modules
│   ├── services/           # Backend API clients & mathematical validators
│   ├── state/              # Global ParallaxContext state provider
│   └── types/              # Full TypeScript definitions for CV pipeline
├── index.html              # HTML entry point with Orbitron & Inter fonts
├── package.json            # Dependencies and scripts
└── vite.config.ts          # Vite configuration with proxy to backend
```

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:3000`.

### 3. Production Build
```bash
npm run build
```

## Backend Integration
The frontend connects seamlessly with the PARALLAX Python CV backend (FastAPI / OpenCV / PyTorch) running on `http://127.0.0.1:8000`.
