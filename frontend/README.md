# Running DragonForge Dashboard & API Server

This folder contains the complete monochromatic research dashboard frontend and backend.

## Structure

- `server/` - Node/Express backend that reads the experimental JSON contracts from the root `results/` folder and exposes them via a REST API.
- `client/` - React (Vite) + Tailwind CSS minimalistic monochromatic dark-mode client dashboard.

## Setup & Running

### Prerequisites

Ensure you have Node.js (>= 18) installed.

### 1. Start the Backend API Server

Navigate to the `server` directory, install dependencies, and run:

```bash
cd frontend/server
npm install
npm run dev
```

The server will start at `http://localhost:3001` and serve routes like `/api/structure/latest`, `/api/continual`, `/api/reasoning`, and `/api/summary`.

### 2. Start the Frontend Client

Navigate to the `client` directory, install dependencies, and run:

```bash
cd frontend/client
npm install
npm run dev
```

The React app will start at `http://localhost:5173` with proxy configuration forwarding `/api` calls directly to the Express server.

## Features

- **Top Navigation & Control Header**: Displays global metadata, instrumented model checkpoint name, and seed value alongside data export functionality.
- **Panel A: Network Topology Inspector**: Beautiful 2D force-directed node-link graph with toggleable control null model.
- **Panel B: Training Evolution Timeline**: Comparison of structural modularity, activation sparsity, and clustering metrics.
- **Panel C: Long-Context Reasoning Benchmark**: Accurate comparisons between BDH Small and parameter-matched Transformers at up to 32k contexts.
- **Panel D: Sequential Continual Learning Matrix**: Flow-based illustration of forgetting and retention comparison.
- **Panel E: Structure ↔ Behavior Bridge**: Highly clinical correlation schematic tracing modular structural layouts to behavioral advantages.
- **Evidence Badges**: Solid, precise, monochromatic badges (`[ESTABLISHED]`, `[MEASURED]`, `[EXPLORATORY]`) applied across all research claim panels.
- **Scale Horizon Protocol collapsing banner**: Elegant bottom disclosure outlining scaling theories for 100M+ scales.
