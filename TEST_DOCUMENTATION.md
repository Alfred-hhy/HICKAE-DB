# Hermes 性能测试文档

## 📋 目录
1. [测试类型说明](#测试类型说明)
2. [测试结果图表详解](#测试结果图表详解)
3. [数据集格式说明](#数据集格式说明)
4. [如何替换数据集](#如何替换数据集)
5. [运行测试](#运行测试)

---

## 测试类型说明

### ⚠️ 重要说明：当前测试是端到端测试，不是模块测试

**当前测试内容：**
- ✅ **端到端系统测试**（End-to-End System Test）
- ❌ **不是**模块化测试（Module-Level Test）

**测试流程：**
```
客户端 (Client)  →  网络 (ZeroMQ)  →  服务器 (Server)  →  返回结果
    ↓                                      ↓
生成加密查询令牌                    解密并搜索加密数据库
(HICKAE_Extract)                   (HICKAE_Decrypt × 数千次)
```

**为什么是端到端测试？**
1. 使用完整的 `server` 和 `client` 程序
2. 测试整个搜索流程：查询生成 → 网络传输 → 服务器搜索 → 结果返回
3. 包含所有组件：密码学操作、网络通信、数据库查询

**立项阶段的建议：**
- 端到端测试可以展示**系统可行性**
- 但应该说明这是**系统级性能测试**，不是单个算法模块测试
- 如果需要模块测试，需要单独编写测试程序（目前编译有问题）

---

## 测试结果图表详解

### 图1: End-to-End Search Latency（端到端搜索延迟）

**文件名：** `1_end_to_end_latency.png`

**测试内容：**
- 从客户端发起搜索请求，到收到服务器返回结果的**总时间**
- 包含：客户端查询生成 + 网络传输 + 服务器搜索 + 结果解析

**测试指标：**
- X 轴：写者数量（3, 5, 7, 10）
- Y 轴：延迟时间（毫秒）

**含义：**
- 这是用户感知的**实际搜索速度**
- 延迟越低，用户体验越好
- 随着写者数量增加，延迟会增加（因为需要搜索更多数据库）

**性能分析：**
- 3 写者：~192 ms
- 10 写者：~396 ms
- 扩展比：2.06x（写者数量增加 3.3x，延迟增加 2.06x）

---

### 图2: Server Processing Latency（服务器处理延迟）

**文件名：** `2_server_latency.png`

**测试内容：**
- 服务器接收到查询令牌后，执行加密搜索的时间
- **核心操作：** 对每个写者的每个关键词执行 `HICKAE_Decrypt` 解密操作

**测试指标：**
- X 轴：写者数量
- Y 轴：服务器处理时间（毫秒）

**含义：**
- 这是**密码学操作的主要开销**
- 服务器需要对每个加密令牌执行配对运算（Pairing-based Cryptography）
- 操作次数 = 写者数量 × 每个写者的关键词数量

**性能分析：**
- 服务器延迟占端到端延迟的 **88-92%**
- 这是系统的主要瓶颈
- 优化方向：并行化、索引优化、分区搜索

---

### 图3: Client Query Generation Time（客户端查询生成时间）

**文件名：** `3_client_query_time.png`

**测试内容：**
- 客户端生成加密搜索令牌的时间
- **核心操作：** 多次调用 `HICKAE_Extract` 生成查询令牌

**测试指标：**
- X 轴：写者数量
- Y 轴：查询生成时间（毫秒）

**含义：**
- 客户端需要为每个写者生成对应的查询令牌
- 包括：分区匹配令牌（Partition Token）+ 关键词匹配令牌（Keyword Token）
- 操作次数与写者数量成正比

**性能分析：**
- 客户端延迟占端到端延迟的 **8-11%**
- 相对较小，不是主要瓶颈
- 3 写者：21 ms，10 写者：32 ms

---

### 图4: Search Latency Breakdown（延迟分解堆叠图）

**文件名：** `4_latency_breakdown.png`

**测试内容：**
- 将端到端延迟分解为三个部分：
  1. **Client Query Generation**（绿色）：客户端生成查询
  2. **Server Processing**（红色）：服务器搜索
  3. **Network + Parsing**（蓝色）：网络传输 + 结果解析

**测试指标：**
- X 轴：写者数量
- Y 轴：时间（毫秒），堆叠显示

**含义：**
- 直观展示各部分的时间占比
- 帮助识别性能瓶颈

**性能分析：**
- **服务器处理**占绝大部分（88-92%）
- **客户端查询生成**占 8-11%
- **网络 + 解析**占 1-2%（几乎可以忽略，因为是本地测试）

---

### 图5: Performance Scaling Factor（性能扩展性）

**文件名：** `5_performance_scaling.png`

**测试内容：**
- 以 3 写者为基线（baseline = 1.0x）
- 计算其他配置相对于基线的延迟倍数

**测试指标：**
- X 轴：写者数量
- Y 轴：归一化延迟（相对于 3 写者）



创建目录：
```bash
mkdir -p my_custom_dataset
```

**步骤2：创建数据文件**

每个写者一个文件，格式如下：
```
# 文件：my_custom_dataset/1.txt
keyword1 doc1 doc2 doc3
keyword2 doc4 doc5
keyword3 doc1 doc6 doc7 doc8
...
```

**示例 Python 脚本：**
```python
import random

num_writers = 5
keywords_per_writer = 50
docs_per_keyword_min = 1
docs_per_keyword_max = 10

keywords = ["email", "report", "meeting", "project", "data", ...]  # 你的关键词列表

for writer_id in range(1, num_writers + 1):
    with open(f"my_custom_dataset/{writer_id}.txt", "w") as f:
        for keyword in random.sample(keywords, keywords_per_writer):
            num_docs = random.randint(docs_per_keyword_min, docs_per_keyword_max)
            doc_ids = random.sample(range(1, 1000), num_docs)
            f.write(f"{keyword} {' '.join(map(str, doc_ids))}\n")
```

**步骤3：修改代码使用新数据集**

编辑 `Hermes/server/server.cpp` 和 `Hermes/client/client.cpp`：
```cpp
// 找到这一行（约第 117 行）：
string database_path = "../../database_small/";

// 修改为：
string database_path = "../../my_custom_dataset/";
```

**步骤4：重新编译并测试**
```bash
cd Hermes
make clean && make
cd ..
./simple_benchmark.sh
```

### 方法3：使用原始 Enron 数据集

**位置：** `database/`（150 个写者，每个数千个关键词）

**警告：**
- 初始化时间：数分钟
- 搜索延迟：数秒
- 仅用于完整系统测试，不适合快速演示

**切换方法：**
```bash
cd Hermes
# 恢复原始配置
cp server/server.cpp.backup server/server.cpp
cp client/client.cpp.backup client/client.cpp
make clean && make
```

---

## 运行测试

### 完整测试流程

**1. 安装依赖**
```bash
pip install -r requirements.txt
```

**2. 运行性能测试**
```bash
./simple_benchmark.sh
```

输出：
- `benchmark_results/search_performance_TIMESTAMP.csv`

**3. 生成综合图表**
```bash
python plot_simple_results.py benchmark_results/search_performance_*.csv
```

输出：
- `benchmark_results/hermes_performance.png`（6 张图的综合图）
- `benchmark_results/performance_report.txt`（性能报告）

**4. 生成单独图表**
```bash
python plot_individual.py benchmark_results/search_performance_*.csv
```

输出：
- `benchmark_results/individual_plots/1_end_to_end_latency.png`
- `benchmark_results/individual_plots/2_server_latency.png`
- `benchmark_results/individual_plots/3_client_query_time.png`
- `benchmark_results/individual_plots/4_latency_breakdown.png`
- `benchmark_results/individual_plots/5_performance_scaling.png`
- `benchmark_results/individual_plots/6_throughput.png`

---

## 测试参数配置

### 修改测试的写者数量

编辑 `simple_benchmark.sh`：
```bash
# 第 8 行
WRITERS=(3 5 7 10)

# 修改为你想要的配置，例如：
WRITERS=(3 5 10 15 20)
```

### 修改测试关键词

编辑 `simple_benchmark.sh`：
```bash
# 第 9 行
KEYWORD="database"

# 修改为你数据集中存在的关键词，例如：
KEYWORD="email"
```

**注意：** 确保关键词在所有写者的数据库中都存在，否则搜索结果为空。

---

## 常见问题

### Q1: 为什么测试这么慢？
**A:** 服务器需要执行大量的配对运算（Pairing-based Cryptography），每次解密需要 100-200 微秒。对于 10 个写者，可能需要执行数千次解密操作。

### Q2: 如何加快测试速度？
**A:**
1. 减少写者数量
2. 减少每个写者的关键词数量
3. 使用小数据集（`database_small/`）

### Q3: 为什么服务器延迟占比这么高？
**A:** 这是加密搜索系统的特点。服务器需要在加密数据上执行搜索，无法像明文搜索那样使用索引优化。

### Q4: 如何进行模块化测试？
**A:** 当前的测试是端到端测试。如果需要模块化测试（单独测试 HICKAE_Encrypt、HICKAE_Decrypt 等），需要：
1. 解决编译依赖问题（emp-tool, pbc 等）
2. 编写独立的测试程序
3. 或者启用 `hickae.hpp` 中被注释的计时代码

### Q5: 数据集中的文档 ID 有什么要求？
**A:**
- 必须是正整数
- 不需要连续
- 同一个文档 ID 可以出现在多个关键词的列表中
- 文档 ID 只是标识符，系统不会实际访问文档内容

---

## 性能优化建议

### 立项演示优化
1. **使用小数据集**（3-10 个写者，50-100 个关键词）
2. **选择常见关键词**（确保有足够的匹配结果）
3. **多次运行取平均值**（减少测量误差）

### 系统性能优化
1. **并行化**：服务器使用多线程并行解密
2. **分区搜索**：启用 `SEARCH_EFFICIENCY` 模式
3. **索引优化**：使用布隆过滤器预筛选
4. **硬件加速**：使用支持 AES-NI 的 CPU

---

## 总结

- **当前测试类型：** 端到端系统测试（不是模块测试）
- **测试内容：** 完整的加密搜索流程
- **主要瓶颈：** 服务器端的密码学操作（88-92% 时间）
- **数据格式：** 倒排索引（keyword doc_id1 doc_id2 ...）
- **替换数据集：** 修改路径并重新编译

**立项建议：**
- 使用小数据集进行演示
- 强调系统可行性，而不是最终性能
- 说明这是端到端测试，展示完整系统功能

**性能分析：**
- 3 写者：1.00x（基线）
- 5 写者：1.23x
- 7 写者：1.37x
- 10 写者：2.06x
- **结论：** 扩展性较好，写者数量增加 3.3x，延迟仅增加 2.06x

**颜色含义：**
- 蓝色：≤ 1.5x（优秀）
- 橙色：1.5x - 2.5x（良好）
- 红色：> 2.5x（需要优化）

---

### 图6: Search Throughput（搜索吞吐量）

**文件名：** `6_throughput.png`

**测试内容：**
- 系统每秒可以处理的查询数量
- 计算公式：吞吐量 = 1000 / 端到端延迟（ms）

**测试指标：**
- X 轴：写者数量
- Y 轴：查询/秒（Queries per Second）

**含义：**
- 评估系统的**处理能力**
- 吞吐量越高，系统可以同时服务更多用户

**性能分析：**
- 3 写者：5.20 查询/秒
- 10 写者：2.52 查询/秒
- 随着写者数量增加，吞吐量下降（因为单次查询延迟增加）

---

## 数据集格式说明

### 数据格式：倒排索引（Inverted Index）

**文件位置：** `database_small/1.txt`, `database_small/2.txt`, ...

**格式：**
```
keyword doc_id1 doc_id2 doc_id3 ...
```

**示例：**
```
invoice 302 562 895
email 93 434 623 792
search 278 363 390 646 708 786 787
```

**含义：**
- 每行代表一个关键词及其出现的文档列表
- `invoice 302 562 895` 表示：关键词 "invoice" 出现在文档 302, 562, 895 中
- 文档 ID 是整数，代表文档的唯一标识符

**为什么是这种格式？**
1. **倒排索引**是搜索引擎的标准数据结构
2. 方便快速查找：给定关键词，立即找到包含该关键词的所有文档
3. Hermes 系统会对这个索引进行**加密**，生成加密令牌

**数据集结构：**
- 每个写者（Writer）有一个独立的数据库文件
- 文件名：`1.txt`, `2.txt`, ..., `N.txt`（N = 写者数量）
- 每个文件包含该写者的所有关键词和文档映射

---

## 如何替换数据集

### 方法1：使用现有的小数据集（推荐用于测试）

**当前使用：** `database_small/`（10 个写者，每个 80 个关键词）

**切换回原始数据集：**
```bash
cd Hermes
# 恢复备份文件
cp server/server.cpp.backup server/server.cpp
cp client/client.cpp.backup client/client.cpp
# 重新编译
make clean && make
```

### 方法2：创建自定义数据集

**步骤1：准备数据**

