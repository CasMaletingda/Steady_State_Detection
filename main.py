import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

# 读取Excel文件
df = pd.read_excel('data.xlsx')

# 时间列转换
if 'Time' in df.columns:
    try:
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    except Exception:
        df['Time'] = pd.to_datetime(df['Time'])
else:
    df['Time'] = range(len(df))

time = df['Time']

# 设置参数
WINDOW = 50
THR_K = 0.05       # 波动阈值比例
SLOPE_K = 0.001    # 斜率阈值比例
RANGE_K = 0.01     # 落差比例

# 设阈值下限，防止出现如果标准差极小导致乘上比例系数所得阈值接近0的情况
STD_MIN = 1e-6
SLOPE_MIN = 1e-8
RANGE_MIN = 1e-8

plots = []

for col in df.columns:
    if col == 'Time':
        continue

    y = df[col].astype(float)

    # 滚动计算稳态区间
    roll_std = y.rolling(WINDOW, center=True, min_periods=1).std()
    roll_slope = (y.diff() / y).rolling(WINDOW, center=True, min_periods=1).mean().abs()
    roll_range = y.rolling(WINDOW, center=True, min_periods=1).max() - y.rolling(WINDOW, center=True, min_periods=1).min()

    # 阈值
    thr_std = max(np.nanstd(y) * THR_K, STD_MIN)
    thr_slope = max(SLOPE_K, SLOPE_MIN)
    thr_range = max(np.nanstd(y) * RANGE_K, RANGE_MIN)

    # 稳态掩码
    if np.nanstd(y) < STD_MIN:
        steady_mask = np.ones_like(y, dtype=bool)
    else:
        steady_mask = (roll_std < thr_std) & (roll_slope < thr_slope) & (roll_range < thr_range) # 判断依据：波动小，斜率小，窗口内的总落差小

    steady_values = y.where(steady_mask, np.nan)

    # 绘图并保存到内存
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_title(col)
    ax.plot(time, y, color='skyblue', label='Original data')
    ax.plot(time, steady_values, color='green', label='Steady')
    ax.set_xlabel("Date_Time")
    ax.set_ylabel("Value")
    ax.grid(axis='y', linestyle='-')
    ax.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plots.append((col, buf))
    plt.close(fig)

# 写入到Excel
output_excel = "绝对稳态.xlsx"
with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
    pd.DataFrame().to_excel(writer, sheet_name='Plots', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Plots']

    row = 0
    for col_name, img_buf in plots:
        worksheet.write(row, 0, col_name)
        worksheet.insert_image(row + 1, 0, col_name + ".png", {'image_data': img_buf, 'x_scale': 0.8, 'y_scale': 0.8})
        row += 25  # 设置图片与图片的间距
