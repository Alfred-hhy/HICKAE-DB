# simhei_plot.py
import matplotlib.pyplot as plt
import matplotlib

# ---------- 1. 无 GUI 后端 ----------
matplotlib.use('Agg')

# ---------- 2. 强制使用 SimHei ----------
plt.rcParams['font.sans-serif'] = ['SimHei']   # 直接指定
plt.rcParams['axes.unicode_minus'] = False   # 负号正常显示

# ---------- 3. 绘图 ----------
x = [1, 2, 3, 4, 5]
y = [10, 20, 25, 30, 22]

plt.figure(figsize=(8, 6))
plt.plot(x, y, 'o-', label='测试数据')
plt.title('中文字体显示测试', fontsize=16)
plt.xlabel('横轴（X）')
plt.ylabel('纵轴（Y）')
plt.legend()
plt.grid(True)

# ---------- 4. 保存 ----------
output_file = '中文字体验证_SimHei.png'
plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
print(f"图片已生成：{output_file}")
plt.close()