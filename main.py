import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage

# 读取 Excel 数据
df = pd.read_excel('data.xlsx')

# 转换时间格式
if 'Time' in df.columns:
    try:
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    except Exception:
        df['Time'] = pd.to_datetime(df['Time'])

# 创建新Excel
wb = Workbook()
ws = wb.active
ws.title = "稳态检测"

current_row = 2

for col in df.columns:
    if col == 'Time':
        continue

    # 创建图像
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(df['Time'], df[col], color='skyblue')
    ax.set_title(col)
    ax.set_xlabel("Date_Time")
    ax.set_ylabel("Value")
    ax.grid(axis='y', linestyle='-')

    # 将绘图保存到内存
    img_stream = BytesIO()
    plt.savefig(img_stream, format='png')
    plt.close(fig)
    img_stream.seek(0)

    # 在新建excel文件中插入图片
    img = XLImage(img_stream)
    img.anchor = f"A{current_row}"
    ws.add_image(img)

    # 设一张图大概占用20行
    current_row += 20

# 保存并命名文件
wb.save("data绘图.xlsx")
print("保存成功。")
