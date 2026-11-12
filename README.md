# Photo Geolocator 01 - Model-Free Python Agent

A model-free street-level photo geolocator agent for the make.fun competition, implemented in Python 3.13 using the standard library only.

## How it Works
1. **Endpoint Integration**: Reads `MAKEFUN_PROMPT_FILE` and queries `${MAKEFUN_ENV_URL}/photos` to retrieve the list of 25 photos (`p01` to `p25`).
2. **JPEG Feature & Header Extraction**: Fetches each JPEG image (`/photos/<id>.jpg`) and extracts header metadata (dimensions, quantization quality tables) and compressed-domain brightness/color proxies without external dependencies (no PIL, no NumPy).
3. **Region Prior & Anchor Mapping**: Uses a curated grid of global geographic anchor points with climate tags (tropical, temperate, cold, desert, mediterranean, mountain) and scores them against extracted image features combined with deterministic trial seeding (`MAKEFUN_TRIAL_SEED`).
4. **Answer Submission**: Posts all 25 latitude/longitude estimates to `${MAKEFUN_ENV_URL}/answers` in the required format.
