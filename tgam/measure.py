import mne
import click
import time
import numpy as np
from TGAMpy.TGAMpy import TGAM
import pandas as pd

@click.command()
@click.option("-p", "--port", required=True, help="COM Port for TGAM")
@click.option("-f", "--sfreq", default=512, help="Sampling frequency (used for EDF/FIF metadata)")
@click.option("-d", "--duration", default=30, help="Recording duration in seconds")
@click.option("-o", "--out", default="export", help="Base output filename (without extension)")
def main(port: str, sfreq: int, duration: int, out: str):
    module = TGAM()
    module.connect(port, timeout=5)

    eeg_buffer = []
    timestamps = []
    start_time = time.time()

    try:
        while time.time() - start_time < duration:
            module.read()

            if module.noise_data:
                noise = module.noise_data.pop()
                if noise != 0:
                    time.sleep(0.001)
                    continue
            else:
                time.sleep(0.001)
                continue

            eeg_sample = module.raw_data
            if eeg_sample is None or not isinstance(eeg_sample, int):
                continue
            print(eeg_sample)
            eeg_buffer.append(eeg_sample)
            timestamps.append(time.time() - start_time)
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    if len(eeg_buffer) == 0:
        print("No data collected.")
        return

    data = np.array([eeg_buffer], dtype=np.float32)
    info = mne.create_info(['EEG 001'], sfreq=sfreq, ch_types=['eeg'])
    raw = mne.io.RawArray(data, info)
    raw.set_meas_date(None)

    raw.export(out + ".edf", fmt='edf', physical_range=(-32768, 32767), overwrite=True)
    raw.save(out + "_raw.fif", overwrite=True)

    pd.DataFrame({
        "timestamp": timestamps,
        "eeg_value": eeg_buffer
    }).to_csv(out + ".csv", index=False)

    print(f"✔ EDF saved: {out}.edf")
    print(f"✔ FIF saved: {out}_raw.fif")
    print(f"✔ CSV saved: {out}.csv")

if __name__ == "__main__":
    main()
