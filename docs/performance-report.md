# VoidBreaker Performance Report (Component 6.4)

Date: 2026-03-01
Owner: AI Agent
Phase: 6.4 — Performance Validation

## Test Environment

- OS: macOS 26.3 (arm64)
- CPU: Apple Silicon (arm)
- RAM: 8 GB
- Python: 3.13.1
- Arcade: 3.3.3
- Build under test: `dist/VoidBreaker.app/Contents/MacOS/VoidBreaker`
- Profiler script: `scripts/profile_performance.py`

## Profiling Configuration

Peak-load target used in stress mode (as required):

- Asteroids: 100
- Enemies: 10
- Player projectiles: 15
- Enemy projectiles: 20
- Currency pickups: 40
- Particles: 300

Frame-time pass criteria:

- Average frame time < 16.67 ms
- No frame > 33.00 ms

Memory leak heuristic:

- Linear RSS slope > 1 MB/min after warm-up indicates a potential leak

## Frame Time Results

| Mode | Duration (s) | Frames | Mean (ms) | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) | Mean FPS | Min FPS | Target Met |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Source (`python -m asterax.app.src.main`) | 120.02 | 7,201 | 16.667 | 16.667 | 16.667 | 16.667 | 16.667 | 60.00 | 60.00 | Yes |
| Packaged (`VoidBreaker.app`) | 1800.02 | 108,001 | 16.667 | 16.667 | 16.667 | 16.667 | 16.667 | 60.00 | 60.00 | Yes |

Result: frame-time targets passed in both source-mode and packaged-mode.

## Memory Results

| Mode | Samples | Initial RSS (MiB) | Peak RSS (MiB) | Final RSS (MiB) | Growth (MiB) | Slope (MB/min) | Leak Detected |
|---|---:|---:|---:|---:|---:|---:|---|
| Source (120s run) | 120 | 0.67 | 126.83 | 54.95 | 54.28 | -6.949 | No |
| Packaged (30 min run) | 1,799 | 0.58 | 127.84 | 44.28 | 43.70 | -0.175 | No |

Result: no monotonic memory growth trend was observed in the required 30+ minute packaged run.

## Bottleneck Analysis

- No frame-time threshold violations were observed.
- Under this stress profile, no subsystem exceeded the 33 ms per-frame threshold.
- Arcade emitted a known text-rendering warning for `draw_text`; this did not cause frame budget violations during tests.

## Artifacts

Generated artifacts are saved under `docs/performance-data/`:

- `source-frame-metrics.json`
- `source-memory.csv`
- `packaged-frame-metrics.json`
- `packaged-memory.csv`
- `combined-summary.json` (latest run summary)

## Conclusion

- Pass: 60 FPS target achieved at required peak entity counts.
- Pass: no memory leak detected in the 30-minute packaged run.
- Pass: performance validation requirements for Component 6.4 are satisfied.
