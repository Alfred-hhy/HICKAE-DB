#!/usr/bin/env python
"""
Hermes Performance Testing - Visualization Script
性能测试结果绘图脚本
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 设置字体 - 不使用中文，避免乱码
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('seaborn-darkgrid')

def plot_search_performance(csv_file, output_dir):
    """绘制搜索性能图"""
    print(f"正在读取数据: {csv_file}")
    df = pd.read_csv(csv_file)

    print(f"数据预览:")
    print(df)
    print()

    # 检查是否有标准差列
    has_std = 'EndToEndStdDev' in df.columns

    # 创建图表
    fig = plt.figure(figsize=(16, 10))

    # 1. 端到端延迟趋势图（带误差棒）
    ax1 = plt.subplot(2, 3, 1)
    if has_std:
        ax1.errorbar(df['Writers'], df['EndToEndLatency(ms)'],
                     yerr=df['EndToEndStdDev'], fmt='o-', linewidth=2.5,
                     markersize=10, color='#2E86AB', capsize=5, capthick=2,
                     label='End-to-End Latency (avg ± std)')
    else:
        ax1.plot(df['Writers'], df['EndToEndLatency(ms)'], 'o-', linewidth=2.5,
                 markersize=10, color='#2E86AB', label='End-to-End Latency')
    ax1.fill_between(df['Writers'], 0, df['EndToEndLatency(ms)'], alpha=0.2, color='#2E86AB')
    ax1.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('End-to-End Search Latency', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=10)
    
    # 2. 服务器延迟趋势图（带误差棒）
    ax2 = plt.subplot(2, 3, 2)
    if has_std:
        ax2.errorbar(df['Writers'], df['ServerLatency(ms)'],
                     yerr=df['ServerStdDev'], fmt='s-', linewidth=2.5,
                     markersize=10, color='#E63946', capsize=5, capthick=2,
                     label='Server Latency (avg ± std)')
    else:
        ax2.plot(df['Writers'], df['ServerLatency(ms)'], 's-', linewidth=2.5,
                 markersize=10, color='#E63946', label='Server Latency')
    ax2.fill_between(df['Writers'], 0, df['ServerLatency(ms)'], alpha=0.2, color='#E63946')
    ax2.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Latency (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Server Processing Latency', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(fontsize=10)

    # 3. 客户端查询生成时间（带误差棒）
    ax3 = plt.subplot(2, 3, 3)
    if has_std:
        ax3.errorbar(df['Writers'], df['ClientQueryTime(ms)'],
                     yerr=df['ClientStdDev'], fmt='^-', linewidth=2.5,
                     markersize=10, color='#06A77D', capsize=5, capthick=2,
                     label='Query Generation (avg ± std)')
    else:
        ax3.plot(df['Writers'], df['ClientQueryTime(ms)'], '^-', linewidth=2.5,
                 markersize=10, color='#06A77D', label='Query Generation')
    ax3.fill_between(df['Writers'], 0, df['ClientQueryTime(ms)'], alpha=0.2, color='#06A77D')
    ax3.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
    ax3.set_title('Client Query Generation Time', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=10)
    
    # 4. 延迟分解堆叠图
    ax4 = plt.subplot(2, 3, 4)
    client_time = df['ClientQueryTime(ms)']
    server_time = df['ServerLatency(ms)']
    network_time = df['EndToEndLatency(ms)'] - df['ClientQueryTime(ms)'] - df['ServerLatency(ms)']
    
    x = np.arange(len(df['Writers']))
    width = 0.6
    
    ax4.bar(x, client_time, width, label='Client Query Gen', alpha=0.8, color='#06A77D')
    ax4.bar(x, server_time, width, bottom=client_time, 
            label='Server Processing', alpha=0.8, color='#E63946')
    ax4.bar(x, network_time, width, 
            bottom=client_time + server_time,
            label='Network + Parsing', alpha=0.8, color='#457B9D')
    
    ax4.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Time (ms)', fontsize=12, fontweight='bold')
    ax4.set_title('Latency Breakdown (Stacked)', fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(df['Writers'])
    ax4.legend(fontsize=9)
    ax4.grid(True, alpha=0.3, axis='y')
    
    # 5. 性能对比（归一化）
    ax5 = plt.subplot(2, 3, 5)
    baseline = df['EndToEndLatency(ms)'].iloc[0]
    normalized = df['EndToEndLatency(ms)'] / baseline
    
    colors = ['#2E86AB' if x <= 1.5 else '#F18F01' if x <= 2.5 else '#E63946' 
              for x in normalized]
    
    bars = ax5.bar(df['Writers'], normalized, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax5.axhline(y=1, color='gray', linestyle='--', linewidth=2, label='Baseline')
    ax5.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Normalized Latency', fontsize=12, fontweight='bold')
    ax5.set_title('Performance Scaling (Normalized)', fontsize=14, fontweight='bold')
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.legend(fontsize=10)
    
    # 在柱子上标注数值
    for bar, val in zip(bars, normalized):
        height = bar.get_height()
        ax5.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}x', ha='center', va='bottom', fontweight='bold')
    
    # 6. 吞吐量估算
    ax6 = plt.subplot(2, 3, 6)
    throughput = 1000.0 / df['EndToEndLatency(ms)']  # 查询/秒
    
    ax6.plot(df['Writers'], throughput, 'D-', linewidth=2.5,
             markersize=10, color='#A23B72', label='Throughput')
    ax6.fill_between(df['Writers'], 0, throughput, alpha=0.2, color='#A23B72')
    ax6.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Queries per Second', fontsize=12, fontweight='bold')
    ax6.set_title('Search Throughput', fontsize=14, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    ax6.legend(fontsize=10)
    
    # 总标题 - 使用英文避免乱码
    fig.suptitle('HICKAG-DB - Search Performance Test', fontsize=18, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    
    output_file = output_dir / 'hermes_performance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 保存图表: {output_file}")
    
    return df

def generate_report(df, output_dir):
    """生成性能报告"""
    report_file = output_dir / 'performance_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("  Hermes 加密数据库性能测试报告\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("测试配置:\n")
        f.write("  - 数据集: database_small (小型测试数据集)\n")
        f.write("  - 测试关键词: database\n")
        f.write(f"  - 写者数量: {df['Writers'].min()} - {df['Writers'].max()}\n\n")
        
        f.write("性能数据:\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'写者数':<8} {'查询生成(ms)':<15} {'服务器(ms)':<15} {'端到端(ms)':<15} {'吞吐量(q/s)':<15}\n")
        f.write("-" * 70 + "\n")
        
        for _, row in df.iterrows():
            throughput = 1000.0 / row['EndToEndLatency(ms)']
            f.write(f"{int(row['Writers']):<8} {row['ClientQueryTime(ms)']:<15.2f} "
                   f"{row['ServerLatency(ms)']:<15.2f} {row['EndToEndLatency(ms)']:<15.2f} "
                   f"{throughput:<15.2f}\n")
        
        f.write("\n性能分析:\n")
        f.write("-" * 70 + "\n")
        
        baseline = df['EndToEndLatency(ms)'].iloc[0]
        worst = df['EndToEndLatency(ms)'].iloc[-1]
        scaling = worst / baseline
        
        f.write(f"  - 基线延迟 (3 写者): {baseline:.2f} ms\n")
        f.write(f"  - 最大延迟 ({int(df['Writers'].iloc[-1])} 写者): {worst:.2f} ms\n")
        f.write(f"  - 性能扩展比: {scaling:.2f}x\n")
        f.write(f"  - 平均服务器占比: {(df['ServerLatency(ms)'] / df['EndToEndLatency(ms)']).mean() * 100:.1f}%\n")
        f.write(f"  - 平均客户端占比: {(df['ClientQueryTime(ms)'] / df['EndToEndLatency(ms)']).mean() * 100:.1f}%\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    print(f"✓ 保存报告: {report_file}")

def main():
    if len(sys.argv) < 2:
        print("用法: python3 plot_simple_results.py <search_csv>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    # 创建输出目录
    output_dir = Path('benchmark_results')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("  Hermes 性能测试结果分析")
    print("=" * 70)
    print()
    
    # 绘制图表
    df = plot_search_performance(csv_file, output_dir)
    
    # 生成报告
    generate_report(df, output_dir)
    
    print()
    print("=" * 70)
    print("  完成！")
    print("=" * 70)
    print(f"输出目录: {output_dir}/")
    print("  - hermes_performance.png (性能图表)")
    print("  - performance_report.txt (性能报告)")

if __name__ == "__main__":
    main()

