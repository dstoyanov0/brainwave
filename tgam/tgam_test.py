import time
from datetime import datetime

from TGAMpy.TGAMpy import TGAM
# import winsound

freq = 440
dur = 1000

module = TGAM()

module.connect("COM9", timeout=5)

highest_att = 0
highest_att_time = datetime.now()

while True:
    module.read()
    if module.noise_data:
        q = module.noise_data.pop()
        if q != 0:
            continue
    else:
        continue
    print(module.band_list)
    if module.raw_data == 0 or module.eAttention == 0 or module.eMeditation == 0:
        continue
    print("Attention: ", module.eAttention)
    if module.eAttention > highest_att:
        highest_att_time = datetime.now()
        highest_att = module.eAttention
    print(f"Highest Att: {highest_att} {highest_att_time.strftime('%H:%M:%S')}")
    print("Raw: ", module.raw_data)
    print(module.band_list)
    print()
    time.sleep(0.2)