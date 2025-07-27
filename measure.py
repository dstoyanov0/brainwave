#!/usr/bin/env python3
import os
import csv
import time
import re
from datetime import datetime, timedelta
from TGAMpy.TGAMpy import TGAM

EXPECTED_KEYS = [
    'delta', 'theta', 'low-alpha', 'high-alpha',
    'low-beta', 'high-beta', 'low-gamma', 'mid-gamma'
]

def parse_bands(band_data):
    if isinstance(band_data, dict):
        bands = []
        for key in EXPECTED_KEYS:
            if key not in band_data:
                return []
            val = band_data[key]
            try:
                bands.append(val.item() if hasattr(val, 'item') else float(val))
            except Exception:
                return []
        return bands
    if isinstance(band_data, (list, tuple)):
        bands = []
        for val in band_data:
            try:
                bands.append(val.item() if hasattr(val, 'item') else float(val))
            except Exception:
                return []
        return bands if len(bands) == len(EXPECTED_KEYS) else []
    if isinstance(band_data, str):
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", band_data)
        if len(nums) >= len(EXPECTED_KEYS):
            try:
                return [float(num) for num in nums[:len(EXPECTED_KEYS)]]
            except Exception:
                return []
    return []

def main():
    module = TGAM()
    module.connect("COM9", timeout=5)
    start_dt = datetime.now()
    start_str = start_dt.strftime('%H%M')
    dir_dt = start_dt if start_dt.hour < 12 else start_dt + timedelta(days=1)
    date_path = dir_dt.strftime('%y/%m/%d')
    base_dir = os.path.join('measurements', date_path)
    os.makedirs(base_dir, exist_ok=True)
    filename = f"eeg_{start_str}_{start_str}_night.csv"
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['timestamp'] + EXPECTED_KEYS)
        try:
            while True:
                try:
                    module.read()
                except Exception:
                    time.sleep(0.1)
                    continue
                if module.noise_data:
                    noise = module.noise_data.pop()
                    if noise != 0:
                        time.sleep(0.1)
                        continue
                raw = module.band_list
                bands = parse_bands(raw)
                if len(bands) != len(EXPECTED_KEYS):
                    time.sleep(0.1)
                    continue
                ts = datetime.utcnow().isoformat()
                writer.writerow([ts] + bands)
                csvfile.flush()
                print(module.band_list)
                time.sleep(60)
        except KeyboardInterrupt:
            end_dt = datetime.now()
            end_str = end_dt.strftime('%H%M')
    new_filename = f"eeg_{start_str}_{end_str}_night.csv"
    new_filepath = os.path.join(base_dir, new_filename)
    os.rename(filepath, new_filepath)
    print(f"✅ Saved EEG data to: {new_filepath}")

if __name__ == '__main__':
    main()
