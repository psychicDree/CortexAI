## Diagrams Project

This project renders architecture diagrams using Mermaid CLI.

Prerequisites
- Node.js 18+

Commands
- Install: `npm install` (no lockfile committed)
- Build: `npm run build` (outputs to `out/`)
- Clean: `npm run clean`

Structure
- `src/dfd.mmd` – Data Flow Diagram
- `out/` – Rendered `.svg` and `.png`

Notes
- Mermaid CLI is executed via `npx` in `render.sh` to avoid global installs.
- Adjust styles and scale flags in `render.sh` as needed.

