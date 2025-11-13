# Hermes 性能测试快速指南

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

需要的包：
- pandas
- matplotlib
- numpy

### 2. 一键运行所有测试
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

这将自动完成：
1. 运行性能测试（测试 3, 5, 7, 10 个写者）
2. 生成综合图表
3. 生成 6 张单独图表
4. 生成性能报告

### 3. 查看结果

**图表：**
- `benchmark_results/hermes_performance.png` - 综合图（6 张图）
- `benchmark_results/individual_plots/` - 单独图表目录
  - `1_end_to_end_latency.png` - 端到端延迟
  - `2_server_latency.png` - 服务器延迟
  - `3_client_query_time.png` - 客户端查询时间
  - `4_latency_breakdown.png` - 延迟分解
  - `5_performance_scaling.png` - 性能扩展性
  - `6_throughput.png` - 吞吐量

**报告：**
- `benchmark_results/performance_report.txt` - 性能分析报告

**文档：**
- `TEST_DOCUMENTATION.md` - 详细测试说明文档

---

## 📊 测试说明

### ⚠️ 重要：这是端到端测试，不是模块测试

当前测试的是**完整系统**（客户端 + 服务器），不是单个密码学模块。

**测试流程：**
```
客户端生成查询 → 网络传输 → 服务器搜索 → 返回结果
```

**适用场景：**
- ✅ 展示系统可行性
- ✅ 评估整体性能
- ✅ 对比不同配置
- ❌ 不适合单独评估密码学算法性能

---

## 📁 文件说明

### 测试脚本
- `simple_benchmark.sh` - 性能测试脚本
- `run_all_tests.sh` - 一键运行所有测试
- `plot_simple_results.py` - 生成综合图表
- `plot_individual.py` - 生成单独图表

### 数据集
- `database_small/` - 小型测试数据集（10 个写者，80 个关键词）
- `database/` - 原始 Enron 数据集（150 个写者，数千个关键词）

### 配置文件
- `requirements.txt` - Python 依赖
- `TEST_DOCUMENTATION.md` - 详细文档

---

## 🔧 自定义测试

### 修改测试的写者数量

编辑 `simple_benchmark.sh`：
```bash
WRITERS=(3 5 7 10)  # 修改为你想要的配置
```

### 修改测试关键词

编辑 `simple_benchmark.sh`：
```bash
KEYWORD="database"  # 修改为你数据集中的关键词
```

### 使用自定义数据集

1. 创建数据集目录和文件（格式见下文）
2. 修改 `Hermes/server/server.cpp` 和 `Hermes/client/client.cpp` 中的路径
3. 重新编译：`cd Hermes && make clean && make`

---

## 📝 数据集格式

### 格式说明

每个写者一个文件，格式为倒排索引：
```
keyword1 doc_id1 doc_id2 doc_id3
keyword2 doc_id4 doc_id5
keyword3 doc_id1 doc_id6 doc_id7
```

### 示例

文件：`database_small/1.txt`
```
invoice 302 562 895
email 93 434 623 792
search 278 363 390 646 708 786 787
```

**含义：**
- `invoice` 关键词出现在文档 302, 562, 895 中
- `email` 关键词出现在文档 93, 434, 623, 792 中

### 创建自定义数据集

使用 `create_small_dataset.py` 作为模板：
```bash
python create_small_dataset.py
```

修改参数：
```python
NUM_WRITERS = 10          # 写者数量
KEYWORDS_PER_WRITER = 80  # 每个写者的关键词数量
DOCS_PER_KEYWORD_MIN = 1  # 每个关键词最少文档数
DOCS_PER_KEYWORD_MAX = 10 # 每个关键词最多文档数
```

---

## 📈 性能结果示例

使用小数据集（10 个写者，80 个关键词）：

| 写者数 | 端到端延迟 | 服务器延迟 | 客户端延迟 | 吞吐量 |
|--------|------------|------------|------------|--------|
| 3      | 192 ms     | 170 ms     | 21 ms      | 5.2 q/s |
| 5      | 236 ms     | 211 ms     | 24 ms      | 4.2 q/s |
| 7      | 264 ms     | 236 ms     | 27 ms      | 3.8 q/s |
| 10     | 396 ms     | 364 ms     | 32 ms      | 2.5 q/s |

**性能分析：**
- 服务器延迟占 88-92%（主要瓶颈）
- 写者数量增加 3.3x，延迟增加 2.06x（扩展性良好）

---

## ❓ 常见问题

### Q: 为什么图表中文显示乱码？
**A:** 已修复。现在所有图表使用英文标题和标签，避免中文乱码问题。

### Q: 如何切换回原始数据集？
**A:** 
```bash
cd Hermes
cp server/server.cpp.backup server/server.cpp
cp client/client.cpp.backup client/client.cpp
make clean && make
```

### Q: 测试太慢怎么办？
**A:** 
1. 减少写者数量（修改 `simple_benchmark.sh` 中的 `WRITERS`）
2. 使用更小的数据集
3. 减少每个写者的关键词数量

### Q: 如何进行模块化测试？
**A:** 当前测试是端到端测试。模块化测试需要：
1. 解决编译依赖问题
2. 编写独立测试程序
3. 或启用 `hickae.hpp` 中被注释的计时代码

详见 `TEST_DOCUMENTATION.md` 的 Q4。

---

## 📚 详细文档

完整的测试说明、图表解释、数据格式说明，请查看：

**[TEST_DOCUMENTATION.md](TEST_DOCUMENTATION.md)**

包含：
- 每个图表的详细解释
- 数据集格式说明
- 如何替换数据集
- 性能优化建议
- 常见问题解答

---

## 🎯 立项演示建议

1. **使用小数据集**（3-10 个写者）
2. **运行多次取平均值**（减少测量误差）
3. **重点展示图表：**
   - 端到端延迟（图1）
   - 性能扩展性（图5）
   - 延迟分解（图4）
4. **说明这是端到端测试**，展示系统可行性
5. **强调加密搜索的特点**：服务器在加密数据上搜索

---

## 📞 支持

如有问题，请查看：
1. `TEST_DOCUMENTATION.md` - 详细文档
2. `benchmark_results/performance_report.txt` - 性能报告
3. 服务器日志：`Hermes/server/server_*.log`

