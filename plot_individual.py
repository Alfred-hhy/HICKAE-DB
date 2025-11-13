#!/usr/bin/env python
"""
Hermes Performance Testing - Individual Plot Generator
为每个性能指标生成单独的图表
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 设置字体
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['axes.unicode_minus'] = False
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    plt.style.use('seaborn-darkgrid')

def plot_end_to_end_latency(df, output_dir):
    """图1: 端到端搜索延迟"""
    plt.figure(figsize=(10, 6))
    plt.plot(df['Writers'], df['EndToEndLatency(ms)'], 'o-', linewidth=3,
             markersize=12, color='#2E86AB', label='End-to-End Latency')
    plt.fill_between(df['Writers'], 0, df['EndToEndLatency(ms)'], alpha=0.2, color='#2E86AB')
    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Latency (ms)', fontsize=14, fontweight='bold')
    plt.title('End-to-End Search Latency vs Number of Writers', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)

    # 添加数值标注
    for i, row in df.iterrows():
        plt.text(row['Writers'], row['EndToEndLatency(ms)'],
                f"{row['EndToEndLatency(ms)']:.1f}ms",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / '1_end_to_end_latency.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {output_file.name}")

def plot_server_latency(df, output_dir):
    """图2: 服务器处理延迟"""
    plt.figure(figsize=(10, 6))
    plt.plot(df['Writers'], df['ServerLatency(ms)'], 's-', linewidth=3,
             markersize=12, color='#E63946', label='Server Processing Latency')
    plt.fill_between(df['Writers'], 0, df['ServerLatency(ms)'], alpha=0.2, color='#E63946')
    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Latency (ms)', fontsize=14, fontweight='bold')
    plt.title('Server Processing Latency vs Number of Writers', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)

    for i, row in df.iterrows():
        plt.text(row['Writers'], row['ServerLatency(ms)'],
                f"{row['ServerLatency(ms)']:.1f}ms",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / '2_server_latency.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {output_file.name}")

def plot_client_query_time(df, output_dir):
    """图3: 客户端查询生成时间"""
    plt.figure(figsize=(10, 6))
    plt.plot(df['Writers'], df['ClientQueryTime(ms)'], '^-', linewidth=3,
             markersize=12, color='#06A77D', label='Client Query Generation')
    plt.fill_between(df['Writers'], 0, df['ClientQueryTime(ms)'], alpha=0.2, color='#06A77D')
    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Time (ms)', fontsize=14, fontweight='bold')
    plt.title('Client Query Generation Time vs Number of Writers', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)

    for i, row in df.iterrows():
        plt.text(row['Writers'], row['ClientQueryTime(ms)'],
                f"{row['ClientQueryTime(ms)']:.1f}ms",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / '3_client_query_time.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {output_file.name}")

def plot_latency_breakdown(df, output_dir):
    """图4: 延迟分解堆叠图"""
    plt.figure(figsize=(10, 6))

    client_time = df['ClientQueryTime(ms)']
    server_time = df['ServerLatency(ms)']
    network_time = df['EndToEndLatency(ms)'] - df['ClientQueryTime(ms)'] - df['ServerLatency(ms)']

    x = np.arange(len(df['Writers']))
    width = 0.6

    p1 = plt.bar(x, client_time, width, label='Client Query Generation', alpha=0.8, color='#06A77D')
    p2 = plt.bar(x, server_time, width, bottom=client_time,
                label='Server Processing', alpha=0.8, color='#E63946')
    p3 = plt.bar(x, network_time, width,
                bottom=client_time + server_time,
                label='Network + Parsing', alpha=0.8, color='#457B9D')

    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Time (ms)', fontsize=14, fontweight='bold')
    plt.title('Search Latency Breakdown (Stacked)', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(x, df['Writers'])
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    output_file = output_dir / '4_latency_breakdown.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {output_file.name}")

def plot_performance_scaling(df, output_dir):
    """图5: 性能扩展性（归一化）"""
    plt.figure(figsize=(10, 6))

    baseline = df['EndToEndLatency(ms)'].iloc[0]
    normalized = df['EndToEndLatency(ms)'] / baseline

    colors = ['#2E86AB' if x <= 1.5 else '#F18F01' if x <= 2.5 else '#E63946'
              for x in normalized]

    bars = plt.bar(df['Writers'], normalized, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=2)
    plt.axhline(y=1, color='gray', linestyle='--', linewidth=2, label='Baseline (3 writers)')
    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Normalized Latency (relative to 3 writers)', fontsize=14, fontweight='bold')
    plt.title('Performance Scaling Factor', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend(fontsize=11)

    for bar, val in zip(bars, normalized):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}x', ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / '5_performance_scaling.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()


def plot_throughput(df, output_dir):
    """图6: 搜索吞吐量"""
    plt.figure(figsize=(10, 6))

    throughput = 1000.0 / df['EndToEndLatency(ms)']

    plt.plot(df['Writers'], throughput, 'D-', linewidth=3,
             markersize=12, color='#A23B72', label='Search Throughput')
    plt.fill_between(df['Writers'], 0, throughput, alpha=0.2, color='#A23B72')
    plt.xlabel('Number of Writers', fontsize=14, fontweight='bold')
    plt.ylabel('Queries per Second', fontsize=14, fontweight='bold')
    plt.title('Search Throughput vs Number of Writers', fontsize=16, fontweight='bold', pad=20)
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12)

    for i, row in df.iterrows():
        tp = 1000.0 / row['EndToEndLatency(ms)']
        plt.text(row['Writers'], tp,
                f"{tp:.2f} q/s",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    output_file = output_dir / '6_throughput.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ {output_file.name}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_individual.py <search_csv>")
        sys.exit(1)

    csv_file = sys.argv[1]

    # 创建输出目录
    output_dir = Path('benchmark_results/individual_plots')
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  Hermes Performance - Individual Plot Generator")
    print("=" * 70)
    print()
    print(f"Reading data: {csv_file}")

    df = pd.read_csv(csv_file)
    print(f"Data points: {len(df)} writer configurations")
    print()

    print("Generating individual plots...")
    plot_end_to_end_latency(df, output_dir)
    plot_server_latency(df, output_dir)
    plot_client_query_time(df, output_dir)
    plot_latency_breakdown(df, output_dir)
    plot_performance_scaling(df, output_dir)
    plot_throughput(df, output_dir)

    print()
    print("=" * 70)
    print("  Complete!")
    print("=" * 70)
    print(f"Output directory: {output_dir}/")
    print(f"Generated 6 individual plots")

if __name__ == "__main__":
    main()
