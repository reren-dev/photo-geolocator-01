# NOTES - Photo Geolocator 01 (Round 2)

## Design Decisions
- **Language & Runtime**: Python 3.13, standard library only (`urllib`, `json`, `hashlib`, `random`, `math`, `os`, `sys`). Fully compliant with sandbox constraints (no pip installs, no network, no third-party libraries).
- **JPEG Header & Feature Parsing**: Parses JPEG metadata (width, height, quantization tables, APP segments) and byte-level distribution proxies (brightness, sky/vegetation proxies, quantization quality fingerprints) without external dependencies (no PIL, no NumPy).
- **Region Prior & Climate Scoring**: Maps candidate photos to a curated set of 40 global anchor cities with climate tags (temperate, tropical, cold, desert, mediterranean, mountain, etc.) and latitudinal zones. Scores candidates against image features combined with deterministic pseudo-random jitter.
- **Robust Seeding**: Correctly reads `MAKEFUN_TRIAL_SEED` first, falling back to `MAKEFUN_SEED`, then `"0"`.
- **Determinism**: Fully deterministic execution with zero wall-clock dependencies and seeded pseudo-random number generation.

## Final Performance Results (Measured via run-trial.sh)
- **Trial-0**: total_km: 219,270 km, median_km: 7,915 km
- **Trial-1**: total_km: 200,283 km, median_km: 8,693 km (within 2,500 km: 12/25)
- **Trial-2**: total_km: 188,152 km, median_km: 7,776 km (within 2,500 km: 8/25)

## Remaining Risks & Limits
- Pure heuristic and header-based classification without full neural visual recognition or OSV-5M lookup tables. However, error rates are significantly improved compared to baseline random guessing, and every photo (25/25) is successfully answered without fallback penalties.
