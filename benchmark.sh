#!/bin/bash
# 自动化性能测试脚本

echo "========================================"
echo "  Hermes 性能测试脚本"
echo "========================================"
echo ""

# 配置参数
WRITERS=(3 5 7 10)  # 测试的写者数量
KEYWORD="database"   # 测试关键词
RESULTS_DIR="benchmark_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建结果目录
mkdir -p $RESULTS_DIR
echo "结果目录: $RESULTS_DIR/"
echo ""

# 输出文件
MODULE_RESULTS="$RESULTS_DIR/module_performance_${TIMESTAMP}.csv"
SEARCH_RESULTS="$RESULTS_DIR/search_performance_${TIMESTAMP}.csv"

# 初始化 CSV 文件
echo "Writers,Setup(ms),KeyGen(ms),IGen(ms),Prep(ms),Encrypt(us),Extract(us)" > $MODULE_RESULTS
echo "Writers,SearchLatency(ms),ServerLatency(ms)" > $SEARCH_RESULTS

echo "========================================"
echo "  第 1 部分: 模块化性能测试"
echo "========================================"
echo ""

# 编译模块测试程序
echo "正在编译模块测试程序..."
cd Hermes
make clean > /dev/null 2>&1

# 编译 test_modules
g++ -march=native -std=c++11 -O2 -pthread -funroll-loops -maes -msse4.2 -mavx2 \
    -I. -I../ -I/home/$USER/Hermes/include -I../include -I/usr/local/include \
    test_modules.cpp -o test_modules \
    -L/home/$USER/Hermes/lib -L/usr/local/lib \
    -lzmq -lgmp -lm -lcrypto -lpbc 2>&1 | grep -v "warning"

if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
else
    echo "✗ 编译失败"
    exit 1
fi

cd ..
echo ""

# 运行模块测试
for n in "${WRITERS[@]}"; do
    echo "测试 $n 个写者..."
    
    OUTPUT=$(Hermes/test_modules $n 100 2>&1)
    
    # 提取性能数据
    SETUP=$(echo "$OUTPUT" | grep "Setup:" | awk '{print $2}')
    KEYGEN=$(echo "$OUTPUT" | grep "KeyGen:" | awk '{print $2}')
    IGEN=$(echo "$OUTPUT" | grep "IGen:" | awk '{print $2}')
    PREP=$(echo "$OUTPUT" | grep "Prep:" | awk '{print $2}')
    ENCRYPT=$(echo "$OUTPUT" | grep "Encrypt:" | awk '{print $2}')
    EXTRACT=$(echo "$OUTPUT" | grep "Extract:" | awk '{print $2}')
    
    # 写入 CSV
    echo "$n,$SETUP,$KEYGEN,$IGEN,$PREP,$ENCRYPT,$EXTRACT" >> $MODULE_RESULTS
    
    echo "  Setup: $SETUP ms, Encrypt: $ENCRYPT μs, Extract: $EXTRACT μs"
    echo ""
done

echo "✓ 模块测试完成，结果保存到: $MODULE_RESULTS"
echo ""

echo "========================================"
echo "  第 2 部分: 端到端搜索性能测试"
echo "========================================"
echo ""

# 编译服务器和客户端
echo "正在编译服务器和客户端..."
cd Hermes
make > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✓ 编译成功"
else
    echo "✗ 编译失败"
    exit 1
fi

cd ..
echo ""

# 运行端到端测试
for n in "${WRITERS[@]}"; do
    echo "测试 $n 个写者的搜索性能..."
    
    # 启动服务器
    cd Hermes/server
    ./server $n > server.log 2>&1 &
    SERVER_PID=$!
    cd ../..
    
    # 等待服务器初始化
    sleep 3
    
    # 运行客户端搜索
    cd Hermes/client
    OUTPUT=$(./client -s $KEYWORD $n 2>&1)
    cd ../..
    
    # 提取延迟数据
    SEARCH_LATENCY=$(echo "$OUTPUT" | grep "End-to-end search latency" | awk '{print $4}')
    SERVER_LATENCY=$(echo "$OUTPUT" | grep "Server search latency" | awk '{print $4}')
    
    # 转换为毫秒
    if [ ! -z "$SEARCH_LATENCY" ]; then
        SEARCH_MS=$(echo "scale=2; $SEARCH_LATENCY / 1000" | bc)
        SERVER_MS=$(echo "scale=2; $SERVER_LATENCY / 1000" | bc)
        
        echo "$n,$SEARCH_MS,$SERVER_MS" >> $SEARCH_RESULTS
        echo "  搜索延迟: $SEARCH_MS ms, 服务器延迟: $SERVER_MS ms"
    else
        echo "  ✗ 测试失败"
    fi
    
    # 停止服务器
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    
    sleep 2
    echo ""
done

echo "✓ 搜索测试完成，结果保存到: $SEARCH_RESULTS"
echo ""

echo "========================================"
echo "  测试完成！"
echo "========================================"
echo ""
echo "结果文件:"
echo "  - 模块性能: $MODULE_RESULTS"
echo "  - 搜索性能: $SEARCH_RESULTS"
echo ""
echo "下一步: 运行 Python 绘图脚本"
echo "  python3 plot_results.py $MODULE_RESULTS $SEARCH_RESULTS"

