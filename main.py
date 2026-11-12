#!/usr/bin/env python3
"""
Photo Geolocator 01 - Model-Free Agent with JPEG Header & Feature Parsing
Standard Library Only (Python 3.13 compatible)
"""

import os
import sys
import json
import urllib.request
import urllib.error
import hashlib
import random
import math

# Enhanced anchor points spanning diverse global regions with climate and region metadata
ANCHORS = [
    {"lat": 37.7749, "lon": -122.4194, "name": "SF", "climate": "temperate", "lat_zone": "mid"},
    {"lat": 40.7128, "lon": -74.0060, "name": "NYC", "climate": "temperate", "lat_zone": "mid"},
    {"lat": 45.5017, "lon": -73.5673, "name": "Montreal", "climate": "cold", "lat_zone": "high"},
    {"lat": 51.0447, "lon": -114.0719, "name": "Calgary", "climate": "cold", "lat_zone": "high"},
    {"lat": 19.4326, "lon": -99.1332, "name": "Mexico City", "climate": "tropical", "lat_zone": "low"},
    {"lat": -15.7975, "lon": -47.8919, "name": "Brasilia", "climate": "tropical_red", "lat_zone": "low"},
    {"lat": -23.5505, "lon": -46.6333, "name": "Sao Paulo", "climate": "subtropical", "lat_zone": "mid_south"},
    {"lat": -34.6037, "lon": -58.3816, "name": "Buenos Aires", "climate": "temperate", "lat_zone": "mid_south"},
    {"lat": -33.4489, "lon": -70.6693, "name": "Santiago", "climate": "arid", "lat_zone": "mid_south"},
    {"lat": 51.5074, "lon": -0.1278, "name": "London", "climate": "temperate_maritime", "lat_zone": "high_mid"},
    {"lat": 48.8566, "lon": 2.3522, "name": "Paris", "climate": "temperate", "lat_zone": "high_mid"},
    {"lat": 52.5200, "lon": 13.4050, "name": "Berlin", "climate": "temperate", "lat_zone": "high_mid"},
    {"lat": 55.7558, "lon": 37.6173, "name": "Moscow", "climate": "cold", "lat_zone": "high"},
    {"lat": 59.3293, "lon": 18.0686, "name": "Stockholm", "climate": "cold", "lat_zone": "high"},
    {"lat": 63.4241, "lon": 10.3981, "name": "Trondheim", "climate": "subarctic", "lat_zone": "polar"},
    {"lat": 40.4168, "lon": -3.7038, "name": "Madrid", "climate": "arid_mediterranean", "lat_zone": "mid"},
    {"lat": 41.9028, "lon": 12.4964, "name": "Rome", "climate": "mediterranean", "lat_zone": "mid"},
    {"lat": 37.9838, "lon": 23.7275, "name": "Athens", "climate": "mediterranean", "lat_zone": "mid"},
    {"lat": 35.6762, "lon": 139.6503, "name": "Tokyo", "climate": "temperate", "lat_zone": "mid"},
    {"lat": 28.6139, "lon": 77.2090, "name": "New Delhi", "climate": "arid_tropical", "lat_zone": "low_mid"},
    {"lat": 27.7172, "lon": 85.3240, "name": "Kathmandu", "climate": "mountain", "lat_zone": "mid"},
    {"lat": -6.2088, "lon": 106.8456, "name": "Jakarta", "climate": "tropical", "lat_zone": "low"},
    {"lat": 3.1390, "lon": 101.6869, "name": "Kuala Lumpur", "climate": "tropical", "lat_zone": "low"},
    {"lat": 13.7563, "lon": 100.5018, "name": "Bangkok", "climate": "tropical", "lat_zone": "low"},
    {"lat": 33.6844, "lon": 73.0479, "name": "Islamabad", "climate": "arid", "lat_zone": "mid"},
    {"lat": 39.9042, "lon": 116.4074, "name": "Beijing", "climate": "temperate", "lat_zone": "mid"},
    {"lat": 24.7136, "lon": 46.6753, "name": "Riyadh", "climate": "desert", "lat_zone": "low_mid"},
    {"lat": 30.0444, "lon": 31.2357, "name": "Cairo", "climate": "desert", "lat_zone": "low_mid"},
    {"lat": 33.5731, "lon": -7.5898, "name": "Casablanca", "climate": "arid_mediterranean", "lat_zone": "mid"},
    {"lat": 6.5244, "lon": 3.3792, "name": "Lagos", "climate": "tropical", "lat_zone": "low"},
    {"lat": -1.2921, "lon": 36.8219, "name": "Nairobi", "climate": "tropical_highland", "lat_zone": "low"},
    {"lat": -26.2041, "lon": 28.0473, "name": "Johannesburg", "climate": "subtropical_arid", "lat_zone": "mid_south"},
    {"lat": -33.8688, "lon": 151.2093, "name": "Sydney", "climate": "temperate_red", "lat_zone": "mid_south"},
    {"lat": -37.8136, "lon": 144.9631, "name": "Melbourne", "climate": "temperate", "lat_zone": "mid_south"},
    {"lat": -41.2865, "lon": 174.7762, "name": "Wellington", "climate": "temperate_maritime", "lat_zone": "mid_south"},
    {"lat": -9.4438, "lon": 147.1803, "name": "Port Moresby", "climate": "tropical", "lat_zone": "low"},
    {"lat": 56.8389, "lon": 60.6057, "name": "Yekaterinburg", "climate": "cold", "lat_zone": "high"},
    {"lat": 61.5240, "lon": 105.3188, "name": "Siberia", "climate": "subarctic", "lat_zone": "polar"},
    {"lat": 42.8746, "lon": 74.5698, "name": "Bishkek", "climate": "mountain", "lat_zone": "mid"},
    {"lat": 33.8547, "lon": 35.8623, "name": "Lebanon", "climate": "mediterranean", "lat_zone": "mid"},
]

def parse_jpeg_metadata(jpeg_bytes):
    """Parse JPEG structure (width, height, quantization tables, APP segments) without external dependencies."""
    width, height = 512, 512
    pos = 2
    q_tables = {}
    
    while pos < len(jpeg_bytes) - 1:
        if jpeg_bytes[pos] != 0xFF:
            pos += 1
            continue
        while pos < len(jpeg_bytes) and jpeg_bytes[pos] == 0xFF:
            pos += 1
        if pos >= len(jpeg_bytes):
            break
        mtype = jpeg_bytes[pos]
        pos += 1
        
        if mtype in (0xD8, 0xD9, 0x01):
            continue
        if 0xD0 <= mtype <= 0xD7:
            continue
            
        if pos + 2 > len(jpeg_bytes):
            break
        length = (jpeg_bytes[pos] << 8) + jpeg_bytes[pos+1]
        
        if mtype in (0xC0, 0xC1, 0xC2): # SOF0, SOF1, SOF2
            if pos + 7 <= len(jpeg_bytes):
                height = (jpeg_bytes[pos+3] << 8) + jpeg_bytes[pos+4]
                width = (jpeg_bytes[pos+5] << 8) + jpeg_bytes[pos+6]
        elif mtype == 0xDB: # DQT
            dqt_data = jpeg_bytes[pos+2:pos+length]
            dqt_pos = 0
            while dqt_pos < len(dqt_data):
                p_tq = dqt_data[dqt_pos]
                tq = p_tq & 0x0F
                precision = (p_tq >> 4) & 0x0F
                dqt_pos += 1
                table_size = 64 if precision == 0 else 128
                if dqt_pos + table_size <= len(dqt_data):
                    q_tables[tq] = dqt_data[dqt_pos:dqt_pos+table_size]
                    dqt_pos += table_size
                else:
                    break
                    
        pos += length
        
    return width, height, q_tables

def extract_features(jpeg_bytes):
    """Extract robust image features: dimensions, quantization characteristics, byte distribution, and hash."""
    size = len(jpeg_bytes)
    width, height, q_tables = parse_jpeg_metadata(jpeg_bytes)
    
    h = hashlib.sha256(jpeg_bytes).digest()
    h_int = int.from_bytes(h[:8], 'big')
    
    # Sample bytes across the file
    step = max(1, size // 512)
    sampled = jpeg_bytes[::step]
    avg_byte = sum(sampled) / len(sampled) if sampled else 128
    
    # Analyze brightness and color distribution proxies
    low_bytes = sum(1 for b in sampled if b < 64)
    mid_bytes = sum(1 for b in sampled if 64 <= b < 192)
    high_bytes = sum(1 for b in sampled if b >= 192)
    
    total_s = len(sampled) or 1
    sky_proxy = high_bytes / total_s
    veg_proxy = low_bytes / total_s
    
    # Quantization table fingerprint (quality proxy)
    q_mean = 0.0
    if q_tables:
        all_q = []
        for tq in q_tables.values():
            all_q.extend(tq)
        if all_q:
            q_mean = sum(all_q) / len(all_q)
            
    return {
        "size": size,
        "width": width,
        "height": height,
        "avg_byte": avg_byte,
        "sky_proxy": sky_proxy,
        "veg_proxy": veg_proxy,
        "q_mean": q_mean,
        "h_int": h_int,
        "hash_bytes": h
    }

def score_anchor(anchor, features, photo_idx):
    """Score an anchor based on image features and region priors."""
    climate = anchor["climate"]
    lat_zone = anchor["lat_zone"]
    
    score = 0.0
    sky = features["sky_proxy"]
    veg = features["veg_proxy"]
    avg_b = features["avg_byte"]
    
    # Heuristic scoring rules
    if climate in ("tropical", "tropical_red") and sky > 0.2:
        score += 3.5
    if climate == "cold" and lat_zone in ("high", "polar"):
        score += 3.5
    if climate == "desert" and avg_b > 135:
        score += 3.5
    if climate in ("temperate", "temperate_maritime", "mediterranean") and 0.15 <= sky <= 0.45:
        score += 3.0
    if climate == "mountain" and veg > 0.3:
        score += 2.5
        
    # Pseudo-random deterministic jitter per photo to diversify guesses across plausible anchors
    h_mix = (features["h_int"] + photo_idx * 131) % 1000 / 1000.0
    score += h_mix * 2.0
    
    return score

def main():
    # 4. Fix the seed: read MAKEFUN_TRIAL_SEED first, fall back to MAKEFUN_SEED, then "0"
    trial_seed = os.environ.get("MAKEFUN_TRIAL_SEED") or os.environ.get("MAKEFUN_SEED") or "0"
    env_url = os.environ.get("MAKEFUN_ENV_URL")
    
    if not env_url:
        print("Error: MAKEFUN_ENV_URL not set", file=sys.stderr)
        sys.exit(1)
        
    env_url = env_url.rstrip("/")
    
    # Seed RNG deterministically
    seed_val = int(hashlib.sha256(str(trial_seed).encode()).hexdigest()[:16], 16)
    rng = random.Random(seed_val)
    
    # Fetch photos list
    photos_url = f"{env_url}/photos"
    try:
        req = urllib.request.Request(photos_url)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            photos = data.get("photos", [])
    except Exception as e:
        print(f"Error fetching photos: {e}", file=sys.stderr)
        sys.exit(1)
        
    answers = []
    
    for idx, p in enumerate(photos):
        pid = p["id"]
        photo_url = f"{env_url}/photos/{pid}.jpg"
        
        lat = 30.0
        lon = 0.0
        
        try:
            req = urllib.request.Request(photo_url)
            with urllib.request.urlopen(req) as resp:
                jpeg_bytes = resp.read()
                
            features = extract_features(jpeg_bytes)
            
            # Score all anchors and pick the best one
            scored_anchors = []
            for anchor in ANCHORS:
                s = score_anchor(anchor, features, idx)
                scored_anchors.append((s, anchor))
                
            scored_anchors.sort(key=lambda x: x[0], reverse=True)
            best_anchor = scored_anchors[0][1]
            
            base_lat = best_anchor["lat"]
            base_lon = best_anchor["lon"]
            
            # Fine-tune jitter based on image features and hash
            h_int = features["h_int"]
            avg_b = features["avg_byte"]
            
            lat_jitter = ((avg_b - 128) / 128.0) * 1.5
            lon_jitter = (((h_int >> 8) % 256) - 128) / 128.0 * 1.5
            
            lat = max(-90.0, min(90.0, base_lat + lat_jitter))
            lon = max(-180.0, min(180.0, base_lon + lon_jitter))
            
        except Exception as e:
            print(f"Error fetching photo {pid}: {e}, using fallback", file=sys.stderr)
            lat = 30.0
            lon = 0.0
            
        answers.append({
            "id": pid,
            "lat": round(lat, 6),
            "lon": round(lon, 6)
        })
        
    # POST answers
    answers_url = f"{env_url}/answers"
    payload = json.dumps({"answers": answers}).encode("utf-8")
    
    try:
        req = urllib.request.Request(
            answers_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            print(f"Answers posted successfully: {result}", file=sys.stderr)
    except Exception as e:
        print(f"Error posting answers: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
