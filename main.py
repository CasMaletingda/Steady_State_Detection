import pandas as pd
import matplotlib.pyplot as plt

# 读取Excel数据
df = pd.read_excel('data.xlsx')

# 解析并转换时间格式
if 'Time' in df.columns:
    try:
        df['Time'] = pd.to_datetime(df['Time'], unit='ms')
    except Exception:
        df['Time'] = pd.to_datetime(df['Time'])

# 绘图
for col in df.columns:
    if col == 'Time':
        continue
    #定义绘图大小
    plt.figure(figsize=(12, 6))
    plt.title(col)
    #取“Time"列作X轴，并取当前一列数据作y轴
    plt.plot(df['Time'], df[col], color='skyblue')
    plt.xlabel("Date_Time")
    plt.ylabel("Value")
    plt.grid(axis='y', linestyle='-')
    plt.show()
