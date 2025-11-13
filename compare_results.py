#!/usr/bin/env python3
"""
对比两种测试方法的结果：
1. 原始方法：每次测试都重启服务器
2. 方案 A：只启动一次服务器，排除服务器启动开销
"""

import pandas as pd
import matplotlib.pyplot as plt
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False

def compare_results(file1, file2):
    """对比两个测试结果"""
    
    # 读取数据
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)
    
    print("=" * 70)
    print("  测试方法对比分析")
    print("=" * 70)
    print()
    print(f"方法 1（重启服务器）: {file1}")
    print(f"方法 2（单服务器）  : {file2}")
    print()
    
    # 创建对比图表
    fig = plt.figure(figsize=(16, 10))
    
    # 1. 端到端延迟对比
    ax1 = plt.subplot(2, 3, 1)
    ax1.plot(df1['Writers'], df1['EndToEndLatency(ms)'], 'o-', linewidth=2.5, 
             markersize=10, color='#E63946', label='Multiple Server Restarts', alpha=0.7)
    ax1.plot(df2['Writers'], df2['EndToEndLatency(ms)'], 's-', linewidth=2.5, 
             markersize=10, color='#2E86AB', label='Single Server (Plan A)', alpha=0.7)
    ax1.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax1.set_ylabel('End-to-End Latency (ms)', fontsize=12, fontweight='bold')
    ax1.set_title('End-to-End Latency Comparison', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 2. 服务器延迟对比
    ax2 = plt.subplot(2, 3, 2)
    ax2.plot(df1['Writers'], df1['ServerLatency(ms)'], 'o-', linewidth=2.5, 
             markersize=10, color='#E63946', label='Multiple Server Restarts', alpha=0.7)
    ax2.plot(df2['Writers'], df2['ServerLatency(ms)'], 's-', linewidth=2.5, 
             markersize=10, color='#2E86AB', label='Single Server (Plan A)', alpha=0.7)
    ax2.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Server Latency (ms)', fontsize=12, fontweight='bold')
    ax2.set_title('Server Latency Comparison', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    # 3. 延迟差异（固定开销估算）
    ax3 = plt.subplot(2, 3, 3)
    diff = df1['EndToEndLatency(ms)'] - df2['EndToEndLatency(ms)']
    ax3.bar(df1['Writers'], diff, color='#F18F01', alpha=0.7, edgecolor='black', linewidth=1.5)
    ax3.axhline(y=diff.mean(), color='red', linestyle='--', linewidth=2, 
                label=f'Average: {diff.mean():.2f} ms')
    ax3.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Latency Difference (ms)', fontsize=12, fontweight='bold')
    ax3.set_title('Fixed Overhead Estimation', fontsize=14, fontweight='bold')
    ax3.legend(fontsize=10)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 4. 归一化对比（相对于 3 个写者）
    ax4 = plt.subplot(2, 3, 4)
    baseline1 = df1['EndToEndLatency(ms)'].iloc[0]
    baseline2 = df2['EndToEndLatency(ms)'].iloc[0]
    norm1 = df1['EndToEndLatency(ms)'] / baseline1
    norm2 = df2['EndToEndLatency(ms)'] / baseline2
    
    ax4.plot(df1['Writers'], norm1, 'o-', linewidth=2.5, markersize=10, 
             color='#E63946', label='Multiple Server Restarts', alpha=0.7)
    ax4.plot(df2['Writers'], norm2, 's-', linewidth=2.5, markersize=10, 
             color='#2E86AB', label='Single Server (Plan A)', alpha=0.7)
    ax4.axhline(y=1, color='gray', linestyle='--', linewidth=2, alpha=0.5)
    ax4.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Normalized Latency', fontsize=12, fontweight='bold')
    ax4.set_title('Performance Scaling (Normalized)', fontsize=14, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3)
    
    # 5. 扩展比对比
    ax5 = plt.subplot(2, 3, 5)
    writers = df1['Writers'].values
    scaling1 = df1['EndToEndLatency(ms)'] / df1['Writers']
    scaling2 = df2['EndToEndLatency(ms)'] / df2['Writers']
    
    ax5.plot(writers, scaling1, 'o-', linewidth=2.5, markersize=10, 
             color='#E63946', label='Multiple Server Restarts', alpha=0.7)
    ax5.plot(writers, scaling2, 's-', linewidth=2.5, markersize=10, 
             color='#2E86AB', label='Single Server (Plan A)', alpha=0.7)
    ax5.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Latency per Writer (ms)', fontsize=12, fontweight='bold')
    ax5.set_title('Scaling Efficiency', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=10)
    ax5.grid(True, alpha=0.3)
    
    # 6. 标准差对比
    ax6 = plt.subplot(2, 3, 6)
    ax6.plot(df1['Writers'], df1['EndToEndStdDev'], 'o-', linewidth=2.5, 
             markersize=10, color='#E63946', label='Multiple Server Restarts', alpha=0.7)
    ax6.plot(df2['Writers'], df2['EndToEndStdDev'], 's-', linewidth=2.5, 
             markersize=10, color='#2E86AB', label='Single Server (Plan A)', alpha=0.7)
    ax6.set_xlabel('Number of Writers', fontsize=12, fontweight='bold')
    ax6.set_ylabel('Standard Deviation (ms)', fontsize=12, fontweight='bold')
    ax6.set_title('Performance Stability', fontsize=14, fontweight='bold')
    ax6.legend(fontsize=10)
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_file = 'benchmark_results/comparison.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ 保存对比图表: {output_file}")
    print()
    
    # 打印统计数据
    print("=" * 70)
    print("  统计分析")
    print("=" * 70)
    print()
    print(f"固定开销估算（延迟差异）:")
    print(f"  平均值: {diff.mean():.2f} ms")
    print(f"  最小值: {diff.min():.2f} ms (at {df1['Writers'].iloc[diff.idxmin()]} writers)")
    print(f"  最大值: {diff.max():.2f} ms (at {df1['Writers'].iloc[diff.idxmax()]} writers)")
    print()
    
    print(f"性能扩展比（3 → 25 写者）:")
    print(f"  方法 1: {norm1.iloc[-1]:.2f}x")
    print(f"  方法 2: {norm2.iloc[-1]:.2f}x")
    print(f"  差异: {abs(norm1.iloc[-1] - norm2.iloc[-1]):.2f}x")
    print()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python compare_results.py <file1> <file2>")
        print("示例: python compare_results.py benchmark_results/search_performance_20251112_220109.csv benchmark_results/search_performance_single_server_20251112_223806.csv")
        sys.exit(1)
    
    compare_results(sys.argv[1], sys.argv[2])

