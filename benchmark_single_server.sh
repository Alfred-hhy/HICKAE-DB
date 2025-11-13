#!/bin/bash
# 方案 A：只启动一次服务器，排除服务器启动的固定开销
# 这样可以更准确地测量搜索性能的扩展性

# 清理函数：确保服务器进程被杀死和端口释放
cleanup() {
    echo "清理残留进程和端口..."
    
    # 方法1: 使用 pkill 匹配路径
    pkill -9 -f "server/server" 2>/dev/null || true
    
    # 方法2: 使用 killall 匹配进程名
    killall -9 server 2>/dev/null || true
    
    # 方法3: 查找并杀死占用端口 8888 的进程
    PORT_PID=$(lsof -ti:8888 2>/dev/null)
    if [ ! -z "$PORT_PID" ]; then
        echo "  发现端口 8888 被进程 $PORT_PID 占用，正在清理..."
        kill -9 $PORT_PID 2>/dev/null || true
    fi
    
    # 等待端口完全释放
    sleep 3
}

# 设置退出时自动清理
trap cleanup EXIT INT TERM

# 启动前先清理一次
cleanup

echo "========================================"
echo "  Hermes 性能测试（方案 A：单服务器）"
echo "========================================"
echo ""
echo "测试方法："
echo "  - 启动服务器一次（25 个写者）"
echo "  - 客户端连续查询不同数量的写者"
echo "  - 排除服务器启动的固定开销"
echo ""

# 配置参数
WRITERS=(19)  # 测试的写者数量
KEYWORD="database"
NUM_RUNS=4  # 每个配置运行的次数（会丢弃第一次）
RESULTS_DIR="benchmark_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建结果目录
mkdir -p $RESULTS_DIR

echo "结果目录: $RESULTS_DIR/"
echo ""

# CSV 文件
SEARCH_RESULTS="$RESULTS_DIR/search_performance_single_server_$TIMESTAMP.csv"

# 编译
echo "========================================"
echo "  编译 Hermes"
echo "========================================"
echo ""
cd Hermes
if [ ! -f "server/server" ] || [ ! -f "client/client" ]; then
    echo "编译中..."
    make clean > /dev/null 2>&1
    make > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "✗ 编译失败"
        exit 1
    fi
    echo "✓ 编译成功"
fi
cd ..

echo ""
echo "========================================"
echo "  启动服务器（25 个写者）"
echo "========================================"
echo ""

# 启动服务器
SERVER_LOG="$RESULTS_DIR/server_single_$TIMESTAMP.log"
cd Hermes/server
./server 25 > ../../$SERVER_LOG 2>&1 &
SERVER_PID=$!
cd ../..

echo "服务器 PID: $SERVER_PID"
echo "服务器日志: $SERVER_LOG"

# 等待服务器初始化（25 个写者需要更长时间）
echo "等待服务器初始化..."
sleep 10

# 检查服务器是否还在运行
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "✗ 服务器启动失败，检查日志:"
    tail -20 $SERVER_LOG
    exit 1
fi

echo "✓ 服务器启动成功"
echo ""

# 创建 CSV 文件头
echo "Writers,ClientQueryTime(ms),EndToEndLatency(ms),ServerLatency(ms),ClientStdDev,EndToEndStdDev,ServerStdDev" > $SEARCH_RESULTS

echo "========================================"
echo "  搜索性能测试"
echo "========================================"
echo ""

# 运行测试
for n in "${WRITERS[@]}"; do
    echo "测试 $n 个写者（运行 $NUM_RUNS 次，丢弃第一次）..."

    # 存储多次运行的结果
    QUERY_TIMES=()
    END_TO_END_TIMES=()
    SERVER_TIMES=()

    # 在开始新的写者配置测试前，等待服务器稳定
    echo "  等待服务器稳定..."
    sleep 3

    # 运行多次
    for run in $(seq 1 $NUM_RUNS); do
        echo "  第 $run/$NUM_RUNS 次运行..."

        # 运行客户端搜索
        cd Hermes/client
        OUTPUT=$(./client -s $KEYWORD $n 2>&1)
        cd ../..

        # 提取性能数据
        QUERY_TIME=$(echo "$OUTPUT" | grep "Time to create search query" | awk '{print $6}')
        END_TO_END=$(echo "$OUTPUT" | grep "End-to-end search latency" | awk '{print $4}')

        # 从服务器日志提取最新的服务器延迟
        # 因为服务器日志会累积，我们需要获取最后一次搜索的延迟
        SERVER_TIME=$(tail -20 $SERVER_LOG | grep "Server search latency" | tail -1 | awk '{print $4}')

        # 检查是否所有数据都提取成功
        if [ -z "$QUERY_TIME" ] || [ -z "$END_TO_END" ] || [ -z "$SERVER_TIME" ]; then
            echo "    ✗ 数据提取失败"
            echo "       QUERY_TIME=$QUERY_TIME, END_TO_END=$END_TO_END, SERVER_TIME=$SERVER_TIME"
            echo "       客户端输出:"
            echo "$OUTPUT" | head -20
            echo "错误：数据解析失败，测试中止"
            kill $SERVER_PID 2>/dev/null
            exit 1
        fi

        # 转换为毫秒（使用 awk 处理科学计数法）
        QUERY_MS=$(awk "BEGIN {printf \"%.2f\", $QUERY_TIME / 1000}")
        END_MS=$(awk "BEGIN {printf \"%.2f\", $END_TO_END / 1000}")
        SERVER_MS=$(awk "BEGIN {printf \"%.2f\", $SERVER_TIME / 1000}")

        # 检查是否有负数（数据错误）
        if (( $(echo "$END_MS < 0" | bc -l) )); then
            echo "    ✗ 检测到负数延迟: $END_MS ms"
            echo "       这表明时间计算出现严重错误"
            echo "错误：数据异常，测试中止"
            kill $SERVER_PID 2>/dev/null
            exit 1
        fi

        # 第一次运行可能包含连接开销，单独标记
        if [ $run -eq 1 ]; then
            echo "    [冷启动] 查询: $QUERY_MS ms, 端到端: $END_MS ms, 服务器: $SERVER_MS ms"
        else
            # 只保存第 2-N 次的结果（排除冷启动）
            QUERY_TIMES+=($QUERY_MS)
            END_TO_END_TIMES+=($END_MS)
            SERVER_TIMES+=($SERVER_MS)
            echo "    [热启动] 查询: $QUERY_MS ms, 端到端: $END_MS ms, 服务器: $SERVER_MS ms"
        fi

        # 等待服务器完全处理完当前请求并重置状态
        # 增加等待时间以避免时间计算错误
        if [ $run -lt $NUM_RUNS ]; then
            echo "    等待服务器重置..."
            sleep 5
        fi
    done

    # 计算平均值和标准差（只使用第 2-N 次的结果）
    if [ ${#QUERY_TIMES[@]} -gt 0 ]; then
        # 将数组转换为逗号分隔的字符串
        QUERY_STR=$(IFS=,; echo "${QUERY_TIMES[*]}")
        END_STR=$(IFS=,; echo "${END_TO_END_TIMES[*]}")
        SERVER_STR=$(IFS=,; echo "${SERVER_TIMES[*]}")

        # 计算平均值
        QUERY_AVG=$(python -c "vals=[$QUERY_STR]; print('%.2f' % (sum(vals)/len(vals)))")
        END_AVG=$(python -c "vals=[$END_STR]; print('%.2f' % (sum(vals)/len(vals)))")
        SERVER_AVG=$(python -c "vals=[$SERVER_STR]; print('%.2f' % (sum(vals)/len(vals)))")

        # 计算标准差
        QUERY_STD=$(python -c "import math; vals=[$QUERY_STR]; avg=sum(vals)/len(vals); print('%.2f' % math.sqrt(sum((x-avg)**2 for x in vals)/len(vals)))")
        END_STD=$(python -c "import math; vals=[$END_STR]; avg=sum(vals)/len(vals); print('%.2f' % math.sqrt(sum((x-avg)**2 for x in vals)/len(vals)))")
        SERVER_STD=$(python -c "import math; vals=[$SERVER_STR]; avg=sum(vals)/len(vals); print('%.2f' % math.sqrt(sum((x-avg)**2 for x in vals)/len(vals)))")

        echo "$n,$QUERY_AVG,$END_AVG,$SERVER_AVG,$QUERY_STD,$END_STD,$SERVER_STD" >> $SEARCH_RESULTS
        echo "  ✓ 平均值（排除冷启动）- 查询: $QUERY_AVG±$QUERY_STD ms, 端到端: $END_AVG±$END_STD ms, 服务器: $SERVER_AVG±$SERVER_STD ms"
    else
        echo "  ✗ 所有测试都失败了，测试中止"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi

    echo ""
done

# 关闭服务器
echo "========================================"
echo "  关闭服务器"
echo "========================================"
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true
echo "✓ 服务器已关闭"
echo ""

echo "========================================"
echo "  测试完成！"
echo "========================================"
echo ""
echo "结果文件: $SEARCH_RESULTS"
echo ""
echo "下一步: 运行 Python 绘图脚本"
echo "  python plot_simple_results.py $SEARCH_RESULTS"
echo "  python plot_individual.py $SEARCH_RESULTS"
echo ""

