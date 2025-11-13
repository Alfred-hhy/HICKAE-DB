#!/bin/bash
# 一键运行所有测试和绘图

echo "========================================"
echo "  Hermes 完整测试流程"
echo "========================================"
echo ""
echo "测试方案："
echo "  方案 A: 单服务器测试（排除服务器启动开销）"
echo ""

# 1. 运行方案 A 测试
echo "[1/4] 运行方案 A 测试（单服务器）..."
./benchmark_single_server.sh

if [ $? -ne 0 ]; then
    echo "✗ 测试失败"
    exit 1
fi

echo ""
echo "========================================"
echo ""

# 2. 生成综合图表
echo "[2/4] 生成综合图表..."
LATEST_CSV=$(ls -t benchmark_results/search_performance_single_server_*.csv | head -1)
echo "使用数据文件: $LATEST_CSV"
python plot_simple_results.py $LATEST_CSV

if [ $? -ne 0 ]; then
    echo "✗ 综合图表生成失败"
    exit 1
fi

echo ""
echo "========================================"
echo ""

# 3. 生成单独图表
echo "[3/4] 生成单独图表..."
python plot_individual.py $LATEST_CSV

if [ $? -ne 0 ]; then
    echo "✗ 单独图表生成失败"
    exit 1
fi

echo ""
echo "========================================"
echo ""

# 4. 如果有旧的测试结果，生成对比图表
echo "[4/4] 检查是否有对比数据..."
OLD_CSV=$(ls -t benchmark_results/search_performance_[0-9]*.csv 2>/dev/null | head -1)

if [ ! -z "$OLD_CSV" ]; then
    echo "发现旧测试数据: $OLD_CSV"
    echo "生成对比图表..."
    python compare_results.py $OLD_CSV $LATEST_CSV

    if [ $? -eq 0 ]; then
        echo "✓ 对比图表生成成功"
    else
        echo "⚠ 对比图表生成失败（不影响主流程）"
    fi
else
    echo "未发现旧测试数据，跳过对比"
fi

echo ""
echo "========================================"
echo "  全部完成！"
echo "========================================"
echo ""
echo "生成的文件："
echo "  - $LATEST_CSV (测试数据)"
echo "  - benchmark_results/hermes_performance.png (综合图)"
echo "  - benchmark_results/performance_report.txt (性能报告)"
echo "  - benchmark_results/individual_plots/*.png (单独图表)"
if [ ! -z "$OLD_CSV" ]; then
    echo "  - benchmark_results/comparison.png (对比图表)"
fi
echo ""
echo "查看文档："
echo "  - TEST_DOCUMENTATION.md (详细说明)"
echo ""

