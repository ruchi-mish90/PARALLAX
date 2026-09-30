from pathlib import Path
import csv

p = Path(r"data\real_pairs\ch2_tmc_nca_20221209T2305274611_d_img_d32\geometry\calibrated\20221209\ch2_tmc_nca_20221209T2305274611_g_grd_d32.csv")

with p.open("r", encoding="utf-8", errors="replace") as f:
    reader = csv.reader(f)
    for i, row in zip(range(5), reader):
        print("ROW", i, "COLUMNS", len(row))
        print(row)
