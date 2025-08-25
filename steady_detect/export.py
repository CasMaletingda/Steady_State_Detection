import os
import pandas as pd
import config as C


def write_plots_excel(plots, out_dir="output", basename="绝对稳态"):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{basename}.xlsx")

    with pd.ExcelWriter(out_path, engine='xlsxwriter', mode='w') as w:
        pd.DataFrame().to_excel(w, sheet_name='Plots', index=False)
        ws = w.sheets['Plots']
        row = 0
        for name, img in plots:
            ws.write(row, 0, name)
            ws.insert_image(row + 1, 0, name + ".png", {'image_data': img, **C.IMG_SCALE})
            row += 25
    return out_path
