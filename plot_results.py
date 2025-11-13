#!/usr/bin/env python3
"""
性能测试结果绘图脚本
用于生成立项演示所需的性能对比图
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

def plot_module_performance(csv_file, output_dir):
    """绘制模块性能图"""
    print(f"正在读取模块性能数据: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # 创建图表
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Hermes 模块化性能测试', fontsize=16, fontweight='bold')
    
    # 1. Setup + KeyGen + IGen + Prep 时间
    ax1 = axes[0, 0]
    x = df['Writers']
    width = 0.6
    
    ax1.bar(x, df['Setup(ms)'], width, label='Setup', alpha=0.8)
    ax1.bar(x, df['KeyGen(ms)'], width, bottom=df['Setup(ms)'], label='KeyGen', alpha=0.8)
    ax1.bar(x, df['IGen(ms)'], width, 
            bottom=df['Setup(ms)'] + df['KeyGen(ms)'], label='IGen', alpha=0.8)
    ax1.bar(x, df['Prep(ms)'], width,
            bottom=df['Setup(ms)'] + df['KeyGen(ms)'] + df['IGen(ms)'], 
            label='Prep', alpha=0.8)
    
    ax1.set_xlabel('Number of Writers', fontsize=12)
    ax1.set_ylabel('Time (ms)', fontsize=12)
    ax1.set_title('Initialization Time Breakdown', fontsize=13, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Encrypt 性能
    ax2 = axes[0, 1]
    ax2.plot(df['Writers'], df['Encrypt(us)'], 'o-', linewidth=2, markersize=8, 
             color='#2E86AB', label='HICKAE Encrypt')
    ax2.set_xlabel('Number of Writers', fontsize=12)
    ax2.set_ylabel('Time (μs)', fontsize=12)
    ax2.set_title('Encryption Performance', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    
    # 3. Extract 性能
    ax3 = axes[1, 0]
    ax3.plot(df['Writers'], df['Extract(us)'], 's-', linewidth=2, markersize=8,
             color='#A23B72', label='HICKAE Extract')
    ax3.set_xlabel('Number of Writers', fontsize=12)
    ax3.set_ylabel('Time (μs)', fontsize=12)
    ax3.set_title('Key Extraction Performance', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend()
    
    # 4. 总初始化时间
    ax4 = axes[1, 1]
    total_init = df['Setup(ms)'] + df['KeyGen(ms)'] + df['IGen(ms)'] + df['Prep(ms)']
    ax4.plot(df['Writers'], total_init, '^-', linewidth=2, markersize=8,
             color='#F18F01', label='Total Initialization')
    ax4.set_xlabel('Number of Writers', fontsize=12)
    ax4.set_ylabel('Time (ms)', fontsize=12)
    ax4.set_title('Total Initialization Time', fontsize=13, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    
    output_file = output_dir / 'module_performance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 保存图表: {output_file}")
    
    return df

def plot_search_performance(csv_file, output_dir):
    """绘制搜索性能图"""
    print(f"正在读取搜索性能数据: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # 创建图表
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle('Hermes 搜索性能测试', fontsize=16, fontweight='bold')
    
    # 1. 端到端搜索延迟
    ax1 = axes[0]
    ax1.plot(df['Writers'], df['SearchLatency(ms)'], 'o-', linewidth=2.5, 
             markersize=10, color='#06A77D', label='End-to-End Latency')
    ax1.fill_between(df['Writers'], 0, df['SearchLatency(ms)'], alpha=0.2, color='#06A77D')
    ax1.set_xlabel('Number of Writers', fontsize=12)
    ax1.set_ylabel('Latency (ms)', fontsize=12)
    ax1.set_title('End-to-End Search Latency', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # 2. 延迟分解
    ax2 = axes[1]
    client_time = df['SearchLatency(ms)'] - df['ServerLatency(ms)']
    
    x = np.arange(len(df['Writers']))
    width = 0.5
    
    ax2.bar(x, df['ServerLatency(ms)'], width, label='Server Processing', 
            alpha=0.8, color='#E63946')
    ax2.bar(x, client_time, width, bottom=df['ServerLatency(ms)'], 
            label='Client + Network', alpha=0.8, color='#457B9D')
    
    ax2.set_xlabel('Number of Writers', fontsize=12)
    ax2.set_ylabel('Time (ms)', fontsize=12)
    ax2.set_title('Latency Breakdown', fontsize=13, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels(df['Writers'])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    output_file = output_dir / 'search_performance.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 保存图表: {output_file}")
    
    return df

def generate_summary_report(module_df, search_df, output_dir):
    """生成性能总结报告"""
    report_file = output_dir / 'performance_summary.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("  Hermes 性能测试总结报告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write("1. 模块性能\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'写者数':<10} {'Encrypt(μs)':<15} {'Extract(μs)':<15} {'初始化(ms)':<15}\n")
        f.write("-" * 60 + "\n")
        
        for _, row in module_df.iterrows():
            total_init = row['Setup(ms)'] + row['KeyGen(ms)'] + row['IGen(ms)'] + row['Prep(ms)']
            f.write(f"{int(row['Writers']):<10} {row['Encrypt(us)']:<15.2f} "
                   f"{row['Extract(us)']:<15.2f} {total_init:<15.2f}\n")
        
        f.write("\n2. 搜索性能\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'写者数':<10} {'端到端延迟(ms)':<20} {'服务器延迟(ms)':<20}\n")
        f.write("-" * 60 + "\n")
        
        for _, row in search_df.iterrows():
            f.write(f"{int(row['Writers']):<10} {row['SearchLatency(ms)']:<20.2f} "
                   f"{row['ServerLatency(ms)']:<20.2f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"✓ 保存报告: {report_file}")

def main():
    if len(sys.argv) < 3:
        print("用法: python3 plot_results.py <module_csv> <search_csv>")
        sys.exit(1)
    
    module_csv = sys.argv[1]
    search_csv = sys.argv[2]
    
    # 创建输出目录
    output_dir = Path('benchmark_results/plots')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("  Hermes 性能测试结果绘图")
    print("=" * 60)
    print()
    
    # 绘制图表
    module_df = plot_module_performance(module_csv, output_dir)
    search_df = plot_search_performance(search_csv, output_dir)
    
    # 生成报告
    generate_summary_report(module_df, search_df, output_dir)
    
    print()
    print("=" * 60)
    print("  绘图完成！")
    print("=" * 60)
    print(f"输出目录: {output_dir}/")
    print("  - module_performance.png")
    print("  - search_performance.png")
    print("  - performance_summary.txt")

if __name__ == "__main__":
    main()

