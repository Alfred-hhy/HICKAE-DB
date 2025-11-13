# Hermes 项目详细说明文档

## 项目概述

### 1. 项目简介
Hermes 是一个**高效且安全的多写者加密数据库**系统的学术原型实现。该项目实现了发表在 IEEE S&P 2025 会议上的论文 "Hermes: Efficient and Secure Multi-Writer Encrypted Database"。

**⚠️ 重要提示**: 这是一个学术概念验证原型，未经过严格的代码审查，**不适合用于生产环境**。

### 2. 核心功能
- **多写者支持**: 支持多个数据写入者同时操作加密数据库
- **加密搜索**: 在加密数据上执行关键词搜索而不泄露信息
- **动态更新**: 支持向加密数据库添加新的关键词和文档
- **高效性能**: 使用分区和优化技术提升搜索效率

---

## 技术架构

### 1. 系统组件

#### 1.1 客户端-服务器架构
```
┌─────────────┐                    ┌─────────────┐
│   Client    │ ←── ZeroMQ ──→    │   Server    │
│  (读者/写者) │                    │ (数据存储)   │
└─────────────┘                    └─────────────┘
```

- **客户端** (`client/client.cpp`): 负责生成搜索查询、更新请求和重建操作
- **服务器** (`server/server.cpp`): 存储加密索引并处理查询请求

#### 1.2 核心密码学组件

**HICKAE (Hierarchical Identity-based Cross-domain Authenticated Encryption)**
- 这是项目的核心加密方案
- 实现在 `hickae.hpp` 文件中
- 基于双线性配对 (Pairing-based Cryptography)

---

## C++ 项目基础知识

### 1. 项目结构说明

```
Hermes/
├── Hermes/                    # 主项目目录
│   ├── client/               # 客户端代码
│   │   ├── client.cpp       # 客户端主程序
│   │   └── words.txt        # 测试用关键词列表
│   ├── server/              # 服务器代码
│   │   └── server.cpp       # 服务器主程序
│   ├── include/             # 头文件目录
│   │   ├── utils.h          # 工具函数
│   │   ├── ThreadPool.h     # 线程池实现
│   │   ├── MurmurHash3.h    # 哈希函数
│   │   └── pbc*.h           # PBC库头文件
│   ├── param/               # 椭圆曲线参数文件
│   ├── config.hpp           # 配置参数
│   ├── types.hpp            # 数据类型定义
│   ├── hickae.hpp           # HICKAE加密方案实现
│   └── Makefile             # 编译配置文件
├── extract_database.go       # 数据库提取工具(Go语言)
└── README.md                 # 项目说明
```

### 2. C++ 头文件 (.hpp/.h) 说明

在 C++ 中，头文件用于声明函数、类和数据结构：

- **`.hpp`**: C++ 头文件，通常包含模板和内联函数的完整实现
- **`.h`**: C 风格头文件，通常只包含声明

**`#pragma once`**: 防止头文件被重复包含的预处理指令

### 3. Makefile 说明

Makefile 是自动化编译工具的配置文件：

```makefile
CC=g++                          # 编译器
CFLAGS=-march=native -std=c++11 -O2 -pthread  # 编译选项
LIBS=-lzmq -lgmp -lm -lcrypto -lpbc           # 链接的库
```

**编译选项解释**:
- `-march=native`: 针对当前CPU优化
- `-std=c++11`: 使用C++11标准
- `-O2`: 优化级别2
- `-pthread`: 启用多线程支持
- `-maes -msse4.2 -mavx2`: 启用硬件加速指令

---

## 依赖库详解

### 1. GMP (GNU Multiple Precision Arithmetic Library)
- **用途**: 大整数运算
- **在项目中的作用**: 处理密码学中的大数运算（如模幂运算）
- **数据类型**: `mpz_t` (多精度整数)

### 2. PBC (Pairing-Based Cryptography Library)
- **用途**: 双线性配对密码学
- **在项目中的作用**: 实现基于配对的加密方案
- **关键概念**:
  - **配对 (Pairing)**: e: G1 × G2 → GT
  - **G1, G2**: 椭圆曲线群
  - **GT**: 目标群
- **数据类型**: `element_t`, `pairing_t`

### 3. ZeroMQ
- **用途**: 高性能异步消息传递
- **在项目中的作用**: 客户端与服务器之间的通信
- **通信模式**: REQ-REP (请求-应答)

### 4. EMP-Toolkit
- **用途**: 高效的密码学协议实现
- **在项目中的作用**: 提供伪随机数生成器 (PRG) 和其他密码学原语

### 5. OpenSSL
- **用途**: 加密和哈希函数
- **在项目中的作用**: 
  - AES加密 (PRF实现)
  - SHA-512哈希
  - 对称加密操作

---

## 核心数据结构

### 1. HICKAE 密钥结构

```cpp
// 私钥结构
struct HICKAE_PrvKey {
    mpz_t tau;              // 主密钥参数
    mpz_t delta;            // 用于身份验证
    mpz_t gamma;            // 类绑定参数
    mpz_t theta;            // 搜索令牌参数
    element_t alpha_to_tau_G1;  // G1群中的元素
};

// 公钥结构
struct HICKAE_PubKey {
    element_t gamma_G2;     // G2群中的gamma
    element_t delta_G2;     // G2群中的delta
    element_t theta_G2;     // G2群中的theta
};
```

### 2. PEKS (Public-key Encryption with Keyword Search) 令牌

```cpp
struct PEKS_Token {
    element_t c1;           // 密文组件1 (G2群)
    element_t c2;           // 密文组件2 (G2群)
    element_t c3;           // 密文组件3 (G2群)
    unsigned char c4[37];   // 加密的消息部分
};
```

### 3. DSSE (Dynamic Searchable Symmetric Encryption) 令牌

```cpp
typedef uint8_t DSSE_Token[37];  // 37字节的令牌
// 结构: [1字节操作标志][4字节文件ID][32字节前一个令牌]
```

### 4. 聚合密钥结构

```cpp
struct PEKS_AggKey {
    mpz_t k1;               // 密钥组件1
    element_t k2;           // 密钥组件2 (G1群)
    element_t k3;           // 密钥组件3 (G1群)
    #ifdef WRITER_EFFICIENCY
    string eepoch;          // 编码的时期信息
    #endif
};
```

---

## 核心算法流程

### 1. HICKAE 加密方案

#### 1.1 系统初始化 (HICKAE_Setup)

**位置**: `hickae.hpp` 第39-128行

**功能**: 初始化系统参数和椭圆曲线配对

**步骤**:
1. 设置大素数 p 和 q (群的阶)
2. 初始化随机数生成器
3. 从参数文件加载椭圆曲线参数 (`d224.param`)
4. 生成主密钥 alpha
5. 加载或生成群生成元 g1 (G1群) 和 g2 (G2群)
6. 计算配对 gt = e(g1, g2)
7. 为每个写者生成公共参数

**关键代码**:
```cpp
// 使用 d224 曲线参数
mpz_set_str(p, "15028799613985034465755506450771561352583254744125520639296541195020", 10);
mpz_set_str(q, "15028799613985034465755506450771561352583254744125520639296541195021", 10);

// 计算配对
element_pairing(gt, g1, g2);
```

#### 1.2 密钥生成 (HICKAE_KeyGen)

**位置**: `hickae.hpp` 第130-185行

**功能**: 生成读者的公私钥对

**步骤**:
1. 生成私钥参数: tau, gamma, delta, theta (都是随机大整数)
2. 计算 alpha^tau 并映射到 G1 群
3. 计算公钥: gamma_G2, delta_G2, theta_G2 (都在 G2 群中)

**密码学原理**:
- 使用离散对数问题的困难性
- 私钥是随机数，公钥是群元素

#### 1.3 写者初始化 (HICKAE_IGen)

**位置**: `hickae.hpp` 第187-207行

**功能**: 为每个写者生成类绑定密钥

**步骤**:
1. 为每个写者生成随机秘密 sigma_prime[i]
2. 计算类绑定密钥: class_binding_key[i] = public_parameters[i] * alpha^(-sigma_prime[i])

#### 1.4 读者预处理 (HICKAE_Prep)

**位置**: `hickae.hpp` 第209-238行

**功能**: 计算写者之间的关联值

**步骤**:
1. 计算每个写者的类秘密: sigma_class[i] = sigma_hat[i] + sigma_prime[i]
2. 计算关联矩阵: correlation[i][j] = g1^(alpha^(tau + sigma_class[i] - sigma_class[j]))

**用途**: 这些关联值用于在搜索时聚合多个写者的密文

#### 1.5 加密 (HICKAE_Encrypt)

**位置**: `hickae.hpp` 第240-291行

**输入**:
- `wid`: 写者ID
- `id`: 标识符 (关键词或分区ID)
- `m`: 要加密的消息 (32字节)

**输出**: PEKS_Token 密文

**步骤**:
1. 生成随机数 r
2. 计算密文组件:
   - c1 = g2^r
   - c2 = theta_G2^r
   - c3 = (gamma_G2 + class_binding_key[wid])^r
3. 计算哈希 h = H(id)，映射到 G1 群
4. 计算 ut = e(h, delta_G2)^r
5. 使用 ut 的哈希值加密消息:
   - c4 = ("VALID" || m) ⊕ H(ut)

**密码学原理**:
- 基于双线性配对的加密
- 使用 "VALID" 标记验证解密正确性

#### 1.6 提取搜索密钥 (HICKAE_Extract)

**位置**: `hickae.hpp` 第293-345行 (单个) 和 第347-413行 (批量)

**功能**: 生成搜索令牌，允许在不解密的情况下搜索

**步骤**:
1. 生成随机 tau_prime
2. 计算聚合密钥:
   - k1 = alpha^tau_prime + theta
   - k2 = h^delta * alpha^(-tau_prime) + gamma * k3 + alpha^tau
   - k3 = Σ(alpha^(tau + sigma_class[i]))
3. 对于写者效率模式，支持批量生成多个时期的密钥

#### 1.7 解密/测试 (HICKAE_Decrypt)

**位置**: `hickae.hpp` 第415-466行

**功能**: 测试密文是否匹配搜索令牌

**步骤**:
1. 计算调整后的 k2: temp = k2 + Σ(correlation[j][wid]) (j ≠ wid)
2. 计算 ut = e(temp, k1*c1 - c2) - e(k3, c3)
3. 使用 H(ut) 解密 c4
4. 验证前5字节是否为 "VALID"
5. 如果验证通过，提取消息部分

**返回**: true (匹配) 或 false (不匹配)

---

### 2. 搜索索引结构

#### 2.1 三层索引架构

```
服务器端索引:
├── EDTkn[writer_id][address]          # DSSE索引 (关键词→文档映射)
├── PTkn[writer_id][partition_addr]    # 分区匹配索引
└── WTkn[writer_id][partition_addr]    # 关键词匹配索引
```

**EDTkn (Encrypted DSSE Tokens)**:
- 存储加密的文档ID链表
- 使用链式结构支持动态更新
- 地址由 PRF(token) 的哈希计算得出

**PTkn (Partition Tokens)**:
- 存储分区匹配的加密令牌
- 支持递归分区结构 (Hermes+)
- 用于快速定位关键词所在分区

**WTkn (Keyword Tokens)**:
- 存储关键词匹配的加密令牌
- 在 WRITER_EFFICIENCY 模式下使用时期树结构
- 支持高效的关键词更新

#### 2.2 分区策略

**标准模式** (SEARCH_EFFICIENCY = 0):
- 单层分区，最多 MAX_PARTITIONS (240) 个分区
- 分区ID = hash(keyword) % MAX_PARTITIONS

**Hermes+ 模式** (SEARCH_EFFICIENCY = 1):
- 递归分区，RECURSIVE_LEVEL (3) 层
- 每层 NUM_PARTITIONS (1000) 个分区
- 每个分区最多 PARTITION_SIZE (10) 个子分区
- 分区ID编码: (hash % num_partitions) << 2 | level

**优势**:
- 减少搜索时需要测试的密文数量
- 提高搜索效率，特别是在大规模数据库中

---

### 3. 搜索流程详解

#### 3.1 客户端搜索 (client.cpp: search函数)

**位置**: `client/client.cpp` 第40-209行

**输入**:
- `writer_subset`: 要搜索的写者ID列表
- `keyword`: 搜索关键词

**步骤**:

**第一步: 生成分区匹配令牌**
```cpp
// Hermes+ 模式: 生成递归分区令牌
array<uint64_t, 2> hash_value = mm_hash(keyword);
uint64_t pid = ((hash_value[0] % NUM_PARTITIONS) << 2) | RECURSIVE_LEVEL;

PEKS_AggKey cp[RECURSIVE_LEVEL];
for (int k = 0; k < RECURSIVE_LEVEL; ++k) {
    HICKAE_Extract(writer_subset, to_string(pid), &cp[k]);
    // 计算下一层分区ID
}
```

**第二步: 生成关键词匹配令牌**
```cpp
#ifdef WRITER_EFFICIENCY
// 生成时期树的所有子节点令牌
vector<string> children_epochs;
// 从当前时期回溯到根节点
for (int i = encoded_epoch.length() - 1; i >= 0; --i) {
    children_epochs.push_back(encoded_epoch.substr(0, i));
}

PEKS_AggKey *cw = new PEKS_AggKey[children_epochs.size()];
for (int i = 0; i < children_epochs.size(); ++i) {
    string id = keyword + children_epochs[i];
    HICKAE_Extract(writer_subset, id, &cw[i]);
}
#endif
```

**第三步: 序列化并发送查询**
- 将令牌序列化为字节流
- 通过 ZeroMQ 发送到服务器

**第四步: 接收并解析结果**
- 接收服务器返回的文档ID列表
- 按写者分组显示结果

#### 3.2 服务器端搜索 (server.cpp: search函数)

**位置**: `server/server.cpp` 第261-730行

**步骤**:

**第一步: 解析搜索令牌**
```cpp
// 解析分区匹配令牌
PEKS_AggKey cp[RECURSIVE_LEVEL];
for (int k = 0; k < RECURSIVE_LEVEL; ++k) {
    mpz_import(cp[k].k1, ...);
    element_from_bytes(cp[k].k2, ...);
    element_from_bytes(cp[k].k3, ...);
}

// 解析关键词匹配令牌
PEKS_AggKey *cw = new PEKS_AggKey[n];
```

**第二步: 多线程并行搜索**
```cpp
ThreadPool pool(MAX_THREADS_SEARCH);
for (int t = 0; t < MAX_THREADS_SEARCH; ++t) {
    threads.push_back(pool.enqueue([&]() {
        // 每个线程处理一个写者的数据库
    }));
}
```

**第三步: 分区匹配 (Hermes+)**
```cpp
string paddr = "";  // 从根分区开始
for (int l = 0; l < RECURSIVE_LEVEL; ++l) {
    found = false;
    // 遍历当前分区的所有子分区
    for (PEKS_Token &eptkn : PTkn[writer_id][paddr]) {
        bool r = HICKAE_Decrypt(writer_subset, writer_id, cp[l], eptkn, m);
        if (r == true) {
            // 找到匹配，提取下一层分区地址
            found = true;
            paddr = extract_partition_address(m);
            break;
        }
    }
    if (!found) break;  // 未找到匹配，停止搜索
}
```

**第四步: 关键词匹配**
```cpp
if (found) {
    vector<int> matches;
    int k = 0;
    // 遍历分区内的所有关键词令牌
    for (Encrypted_Search_Token &ewtkn : WTkn[writer_id][paddr]) {
        // 尝试用不同时期的令牌解密
        for (int i = 0; i < n; ++i) {
            if (ewtkn.data.find(cw[i].eepoch) != ewtkn.data.end()) {
                bool r = HICKAE_Decrypt(writer_subset, writer_id, cw[i],
                                       ewtkn.data[cw[i].eepoch], m);
                if (r == true) {
                    matches.push_back(k);
                    break;
                }
            }
        }
        ++k;
    }

    // 找到最新的匹配 (最大索引)
    int latest_match = max(matches);
    if (latest_match >= 0) {
        // 提取DSSE搜索令牌
        memcpy(search_token, m + 5, 32);

        // 清理过时的令牌
        for (int match : matches) {
            if (match != latest_match) {
                WTkn[writer_id][paddr].erase(...);
            }
        }
    }
}
```

**第五步: DSSE链式搜索**
```cpp
if (found) {
    int count = 0;
    while (1) {
        // 计算地址: addr = H(search_token)[0:10]
        SHA512_Update(&sha512, search_token, 16);
        SHA512_Final(tmp, &sha512);

        // 查找DSSE索引
        if (EDTkn[writer_id].find(addr) != EDTkn[writer_id].end()) {
            DSSE_Token value = EDTkn[writer_id][addr];

            // 解密: value ⊕ H(search_token)[10:47]
            for (int i = 0; i < 37; ++i)
                value[i] ^= tmp[i+10];

            // 提取文档ID
            memcpy(&output[writer_id][count+1], value + 1, sizeof(int));
            count++;

            // 获取前一个令牌，继续链式搜索
            memcpy(search_token, value + 5, 32);
        } else {
            break;  // 到达链表末尾
        }
    }
    output[writer_id][0] = count;
}
```

**第六步: 返回结果**
```cpp
// 序列化所有写者的结果
zmq::message_t search_outcome(...);
for (int writer_id : writer_subset) {
    memcpy(data, &output[writer_id][0], sizeof(int));  // 文档数量
    for (int k = 1; k <= output[writer_id][0]; ++k) {
        memcpy(data, &output[writer_id][k], sizeof(int));  // 文档ID
    }
}
socket_server->send(search_outcome);
```

---

### 4. 更新流程详解

#### 4.1 客户端更新 (client.cpp: update函数)

**位置**: `client/client.cpp` 第211-520行

**输入**:
- `writer_id`: 写者ID
- `file_id`: 新文档ID
- `num_updates`: 更新的关键词数量

**步骤**:

**第一步: 加载本地状态**
```cpp
unordered_map<string, uint64_t> state;
// 从数据库文件读取每个关键词的当前状态计数
```

**第二步: 生成DSSE更新令牌**
```cpp
for (int i = 0; i < num_updates; ++i) {
    // 读取关键词
    getline(updated_file, keyword);

    // 生成当前令牌: token = PRF(keyword || state[keyword], writer_key)
    string seed = keyword + to_string(state[keyword]);
    prf(seed, writer_secret_key, token);

    // 计算地址: addr = H(token)[0:10]
    SHA512_Update(&sha512, token, 16);
    SHA512_Final(tmp, &sha512);

    // 创建DSSE值: [操作标志][文件ID][前一个令牌]
    DSSE_Token value;
    value[0] = 1;  // 1 = 添加, 0 = 删除
    memcpy(value + 1, &file_id, sizeof(int));
    memcpy(value + 5, prev_token, 32);

    // 加密: value ⊕ H(token)[10:47]
    for (int j = 0; j < 37; ++j)
        value[j] ^= tmp[j+10];
}
```

**第三步: 生成分区令牌 (Hermes+)**
```cpp
#ifdef SEARCH_EFFICIENCY
// 计算分区ID
array<uint64_t, 2> hash_value = mm_hash(keyword);
uint64_t pid = ((hash_value[0] % NUM_PARTITIONS) << 2) | RECURSIVE_LEVEL;

// 计算分区标签
unsigned char partition_tag[32];
prf(&pid, sizeof(pid), writer_secret_key, partition_tag);

// 加密分区标签
PEKS_Token eptkn;
HICKAE_Encrypt(writer_id, to_string(pid), partition_tag, &eptkn);
#endif
```

**第四步: 生成关键词令牌**
```cpp
#ifdef WRITER_EFFICIENCY
// 为时期树的所有祖先节点生成令牌
Encrypted_Search_Token ewtkn;
for (int i = 0; i < gamma_t.size(); ++i) {
    string id = keyword + gamma_t[i];
    HICKAE_Encrypt(writer_id, id, token, &ewtkn.data[gamma_t[i]]);
}
#else
// 只为当前时期生成令牌
string id = keyword + to_string(epoch);
PEKS_Token ewtkn;
HICKAE_Encrypt(writer_id, id, prev_token, &ewtkn);
#endif
```

**第五步: 发送更新请求**
```cpp
zmq::message_t update_query(...);
// 序列化: [操作码'U'][writer_id][num_updates][更新数据...]
socket_client->send(update_query);
```

#### 4.2 服务器端更新 (server.cpp: update函数)

**位置**: `server/server.cpp` 第732-998行

**步骤**:

**第一步: 解析更新请求**
```cpp
int writer_id, num_updates;
memcpy(&writer_id, update_query, 4);
memcpy(&num_updates, update_query + 4, 4);
```

**第二步: 更新DSSE索引**
```cpp
for (int i = 0; i < num_updates; ++i) {
    char addr[21];
    DSSE_Token value;

    memcpy(addr, update_query, 20);
    memcpy(value, update_query + 20, 37);

    // 插入到DSSE索引
    EDTkn[writer_id][addr] = value;
}
```

**第三步: 更新分区索引 (Hermes+)**
```cpp
#ifdef SEARCH_EFFICIENCY
string paddr;
memcpy(paddr, update_query, 20);

PEKS_Token eptkn;
element_from_bytes(eptkn.c1, update_query);
element_from_bytes(eptkn.c2, update_query + 168);
element_from_bytes(eptkn.c3, update_query + 336);
memcpy(eptkn.c4, update_query + 504, 37);

// 只在分区首次创建时添加
if (PTkn[writer_id][paddr].empty()) {
    PTkn[writer_id][""].push_back(eptkn);
}
#endif
```

**第四步: 更新关键词索引**
```cpp
#ifdef WRITER_EFFICIENCY
Encrypted_Search_Token ewtkn;
for (int i = 0; i < n; ++i) {
    PEKS_Token token;
    // 反序列化令牌
    ewtkn.data[eepoch[i]] = token;
}
WTkn[writer_id][paddr].push_back(ewtkn);
#else
PEKS_Token ewtkn;
// 反序列化令牌
WTkn[writer_id][paddr].push_back(ewtkn);
#endif
```

**第五步: 发送确认**
```cpp
zmq::message_t ack("ACK");
socket_server->send(ack);
```

---

### 5. 时期管理 (Epoch Management)

#### 5.1 时期编码

**标准模式**:
- 简单递增: epoch = 1, 2, 3, ...
- 每次更新后 epoch++

**写者效率模式** (WRITER_EFFICIENCY):
- 使用二叉树编码
- 深度: DEPTH_EPOCH_TREE (63)
- 编码规则:
  - 空字符串 → "1"
  - "1" → "11"
  - "11" → "111"
  - "111" → "112"
  - "112" → "1121"
  - ...

**编码函数** (`types.hpp` 第50-59行):
```cpp
string encode_epoch(string prev_encoded_e) {
    if (prev_encoded_e.length() == DEPTH_EPOCH_TREE) {
        // 已达最大深度，回溯并增加
        for (int i = DEPTH_EPOCH_TREE - 1; i >= 0; --i) {
            if ((prev_encoded_e.substr(0, i) + "1") == prev_encoded_e.substr(0, i + 1)) {
                return prev_encoded_e.substr(0, i) + "2";
            }
        }
    }
    return prev_encoded_e + "1";  // 添加新子节点
}
```

#### 5.2 时期树的优势

**问题**: 在标准模式下，每次更新都需要为新时期生成令牌，导致索引大小线性增长

**解决方案**: 使用时期树
- 每个节点代表一个时期
- 搜索时只需测试从当前节点到根的路径上的令牌
- 路径长度 = O(log epoch)，而不是 O(epoch)

**示例**:
```
时期序列: 1, 2, 3, 4, 5
编码:     "", "1", "11", "111", "112"

时期树:
    ""
    └── "1"
        └── "11"
            ├── "111"
            └── "112"

搜索时期5时，测试路径: "112" → "11" → "1" → ""
```

---

## 配置参数详解

### 1. config.hpp 参数说明

**位置**: `Hermes/config.hpp`

```cpp
// 密码学参数
const int NUM_BITS = 224;              // 随机数位数 (224位安全性)
const int MAX_KEYWORDS = 100;          // 每个写者的最大关键词数

// 线程配置
const int MAX_THREADS_INIT = 8;        // 初始化时的最大线程数
const int MAX_THREADS_SEARCH = 8;      // 搜索时的最大线程数
const int MAX_THREADS_UPDATE = 4;      // 更新时的最大线程数
const int MAX_THREADS_REBUILD = 4;     // 重建时的最大线程数

// 网络配置
const int SERVER_PORT = 8888;          // 服务器监听端口

// 索引参数
const int MAX_PARTITIONS = 240;        // 最大分区数 (基于最大数据库57,639关键词)
const int MAX_TOKEN_SIZE = 148;        // 令牌最大字节数
const int MAX_MATCH_OUTPUT = 4096;     // 最大匹配输出数

// Hermes+ 参数
const int RECURSIVE_LEVEL = 3;         // 递归分区层数
const int PARTITION_SIZE = 10;         // 每个分区的子分区数
const int NUM_PARTITIONS = 1000;       // 每层的分区数

// 功能开关
#define ENABLE_SEPARATE_SEARCH  1      // 启用独立搜索 (每个写者单独线程)
#define WRITER_EFFICIENCY       1      // 启用写者效率优化 (时期树)
#define SEARCH_EFFICIENCY       1      // 启用搜索效率优化 (递归分区)
```

### 2. 编译时配置

#### 2.1 启用/禁用 Hermes+

**修改**: `config.hpp` 第21行

```cpp
// 禁用 Hermes+ (标准模式)
// #define SEARCH_EFFICIENCY       1

// 启用 Hermes+ (递归分区)
#define SEARCH_EFFICIENCY       1
```

**重新编译**:
```bash
cd Hermes
make clean
make
```

#### 2.2 调整线程数

**修改**: `config.hpp` 第4-7行

```cpp
const int MAX_THREADS_INIT      = 16;  // 增加到16线程
const int MAX_THREADS_SEARCH    = 16;
```

**注意**: 线程数应根据CPU核心数调整，过多线程可能导致性能下降

#### 2.3 修改服务器地址

**客户端修改**: `client/client.cpp` 第678行

```cpp
// 本地测试
string server_address = "tcp://127.0.0.1:" + to_string(SERVER_PORT);

// 远程服务器
string server_address = "tcp://192.168.1.100:" + to_string(SERVER_PORT);
```

**重新编译客户端**:
```bash
make client
```

---

## 数据库准备

### 1. Enron 邮件数据集

**下载地址**: https://www.cs.cmu.edu/~enron/

**数据集说明**:
- 包含约50万封邮件
- 来自150个邮箱
- 用于测试多写者场景

### 2. 数据提取工具

**工具**: `extract_database.go`

**功能**: 从 Enron 邮件数据集提取关键词-文档倒排索引

**使用步骤**:

```bash
# 1. 下载并解压 Enron 数据集，得到 maildir 文件夹

# 2. 将 extract_database.go 放在与 maildir 同级目录

# 3. 安装 Go 依赖
go env -w GO111MODULE=off
go get github.com/montanaflynn/stats

# 4. 运行提取工具
go run extract_database.go
```

**输出**: `database/` 文件夹，包含多个文本文件

**文件格式** (例如 `1.txt`):
```
university 42 156 289 ...
security 15 78 234 ...
enron 1 2 3 4 5 ...
```
- 每行: `关键词 文档ID1 文档ID2 ...`
- 文件名: `<writer_id>.txt`

### 3. 数据提取原理

**位置**: `extract_database.go` 第93-191行

**步骤**:

1. **遍历邮箱文件夹**:
```go
senderFolders, _ := ioutil.ReadDir("./maildir/")
for _, sender := range senderFolders {
    // 处理每个发件人的邮件
}
```

2. **提取关键词**:
```go
// 读取邮件内容
content, _ := ioutil.ReadFile(emailPath)

// 分词并过滤停用词
words := strings.Fields(string(content))
for _, word := range words {
    if !stopwords[word] && len(word) > 3 {
        keywords[word] = append(keywords[word], fileID)
    }
}
```

3. **去重和排序**:
```go
// 去除重复的文档ID
keywords[word] = removeDuplicateInt(keywords[word])
```

4. **写入文件**:
```go
for keyword, fileIDs := range keywords {
    fmt.Fprintf(file, "%s", keyword)
    for _, id := range fileIDs {
        fmt.Fprintf(file, " %d", id)
    }
    fmt.Fprintf(file, "\n")
}
```

---

## 编译和运行

### 1. 环境准备

#### 1.1 自动安装依赖

```bash
chmod +x auto_setup.sh
./auto_setup.sh
```

**脚本功能**:
- 安装 GMP 库
- 安装 PBC 库
- 安装 ZeroMQ 库
- 安装 EMP-Toolkit

#### 1.2 手动安装 (如果自动安装失败)

**GMP**:
```bash
wget https://gmplib.org/download/gmp/gmp-6.2.1.tar.xz
tar -xf gmp-6.2.1.tar.xz
cd gmp-6.2.1
./configure --prefix=$HOME/Hermes
make
make install
```

**PBC**:
```bash
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xf pbc-0.5.14.tar.gz
cd pbc-0.5.14
./configure --prefix=$HOME/Hermes
make
make install
```

**ZeroMQ**:
```bash
# 安装 libzmq
sudo apt-get install libzmq3-dev

# 安装 cppzmq (仅头文件)
git clone https://github.com/zeromq/cppzmq.git
sudo cp cppzmq/*.hpp /usr/local/include/
```

**EMP-Toolkit**:
```bash
git clone https://github.com/emp-toolkit/emp-tool.git
cd emp-tool
cmake .
make
sudo make install
```

### 2. 编译项目

```bash
cd Hermes

# 清理旧的编译文件
make clean

# 编译服务器和客户端
make

# 或者单独编译
make server   # 只编译服务器
make client   # 只编译客户端
```

**编译输出**:
- `server/server`: 服务器可执行文件
- `client/client`: 客户端可执行文件

### 3. 运行服务器

```bash
cd server

# 使用默认参数 (25个写者)
./server

# 指定写者数量 (例如150个)
./server 150
```

**服务器输出**:
```
===================== Initialization =====================
Encoded epoch:
Writer ID: 1
Writer ID: 2
...
Thread 0 ends.
Thread 1 ends.
...
Done
```

**初始化过程**:
1. 加载椭圆曲线参数
2. 生成密钥
3. 多线程加载数据库文件
4. 构建加密索引
5. 等待客户端连接

### 4. 运行客户端

#### 4.1 搜索操作

```bash
cd client

# 搜索关键词 "university"，在所有写者的数据库中
./client -s university

# 搜索关键词 "security"，在前50个写者的数据库中
./client -s security 50

# 搜索关键词 "enron"，在前100个写者的数据库中
./client -s enron 100
```

**输出示例**:
```
===================== Initialization =====================
Connected to the server at the address tcp://127.0.0.1:8888
Finished reader and writers setup
===================== Search query ======================
Time to create search query: 0.123 ms
Keyword "university" appears in:
Writer 1: 42 156 289 ...
Writer 2: 15 78 234 ...
...
End-to-end search latency: 45.67 ms
```

#### 4.2 更新操作

```bash
cd client

# 更新25个关键词
./client -u 25

# 更新100个关键词
./client -u 100
```

**输出示例**:
```
===================== Initialization =====================
...
===================== Search query ======================
Keyword "security" appears in:
Writer 1: 10 20 30
...
===================== Update query ======================
Time to create update query: 1.234 ms
End-to-end update latency: 12.34 ms
===================== Search query ======================
Keyword "security" appears in:
Writer 1: 10 20 30 2025  # 新增的文档ID
...
```

**更新流程**:
1. 搜索关键词 "security" (更新前)
2. 执行更新操作 (添加新文档)
3. 再次搜索 "security" (验证更新)

#### 4.3 重建操作

```bash
cd client

# 执行重建操作
./client -r
```

**重建功能**: 清理过时的索引条目，优化存储空间

---

## 性能优化技巧

### 1. 线程数调优

**原则**: 线程数 ≈ CPU核心数

**测试方法**:
```bash
# 查看CPU核心数
nproc

# 修改 config.hpp
const int MAX_THREADS_SEARCH = 16;  # 设置为核心数

# 重新编译并测试
make clean && make
```

### 2. 分区参数调优

**Hermes+ 参数**:
```cpp
const int RECURSIVE_LEVEL = 3;      // 层数: 2-4
const int PARTITION_SIZE = 10;      // 子分区数: 5-20
const int NUM_PARTITIONS = 1000;    // 分区数: 100-10000
```

**权衡**:
- 更多层数 → 更快搜索，但更多加密开销
- 更大分区 → 更少加密，但更慢搜索

### 3. 内存优化

**问题**: 大规模数据库可能导致内存不足

**解决方案**:
1. 减少 `MAX_MATCH_OUTPUT` (限制单次搜索结果数)
2. 使用磁盘存储代替内存索引 (需修改代码)
3. 增加系统交换空间

### 4. 网络优化

**本地测试**: 使用 `127.0.0.1` (回环地址)

**远程测试**:
- 使用千兆以太网或更快网络
- 考虑使用 ZeroMQ 的压缩选项
- 批量处理多个查询

---

## 常见问题解答

### 1. 编译错误

**问题**: `fatal error: pbc.h: No such file or directory`

**解决**:
```bash
# 检查 PBC 是否正确安装
ls ~/Hermes/include/pbc.h

# 如果不存在，重新安装 PBC
cd pbc-0.5.14
./configure --prefix=$HOME/Hermes
make install

# 修改 Makefile 中的路径
INCLUDE_PATH=-I/home/$(USER)/Hermes/include
```

**问题**: `undefined reference to 'zmq_ctx_new'`

**解决**:
```bash
# 安装 ZeroMQ 开发库
sudo apt-get install libzmq3-dev

# 或手动编译安装
git clone https://github.com/zeromq/libzmq.git
cd libzmq
./autogen.sh
./configure --prefix=$HOME/Hermes
make install
```

### 2. 运行时错误

**问题**: `error opening parameter file`

**解决**:
```bash
# 确保参数文件存在
ls Hermes/param/d224.param
ls Hermes/param/g1
ls Hermes/param/g2

# 确保从正确目录运行
cd Hermes/server
./server
```

**问题**: `Connection refused`

**解决**:
```bash
# 确保服务器正在运行
ps aux | grep server

# 检查端口是否被占用
netstat -tuln | grep 8888

# 修改端口 (如果需要)
# config.hpp: const int SERVER_PORT = 9999;
```

### 3. 性能问题

**问题**: 搜索速度很慢

**解决**:
1. 启用 Hermes+ 模式 (`SEARCH_EFFICIENCY = 1`)
2. 增加线程数
3. 减少搜索的写者数量
4. 使用更快的CPU和更多内存

**问题**: 初始化时间过长

**解决**:
1. 增加 `MAX_THREADS_INIT`
2. 减少数据库大小
3. 使用SSD存储数据库文件

### 4. 数据库问题

**问题**: `database/1.txt` 不存在

**解决**:
```bash
# 确保已运行数据提取工具
go run extract_database.go

# 检查输出
ls database/

# 手动创建测试数据库
mkdir -p Hermes/database
echo "test 1 2 3" > Hermes/database/1.txt
```

---

## 代码深度解读

### 1. 关键代码片段分析

#### 1.1 PRF (伪随机函数) 实现

**位置**: `include/utils.h` 第106-131行

```cpp
int prf(unsigned char *seed, int seed_len, unsigned char *key, unsigned char *output) {
    EVP_CIPHER_CTX *ctx;
    int len, ciphertext_len;

    // 创建加密上下文
    if(!(ctx = EVP_CIPHER_CTX_new()))
        handleErrors();

    // 使用 AES-256-CBC 模式
    if(1 != EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, NULL))
        handleErrors();

    // 加密种子
    if(1 != EVP_EncryptUpdate(ctx, output, &len, seed, seed_len))
        handleErrors();
    ciphertext_len = len;

    // 完成加密
    if(1 != EVP_EncryptFinal_ex(ctx, output + len, &len))
        handleErrors();
    ciphertext_len += len;

    // 清理
    EVP_CIPHER_CTX_free(ctx);

    return ciphertext_len;
}
```

**解释**:
- **PRF**: 将任意长度输入映射到固定长度输出的确定性函数
- **实现**: 使用 AES-256-CBC 加密
- **用途**: 生成搜索令牌、分区标签等
- **安全性**: 基于 AES 的安全性，输出不可区分于随机

#### 1.2 MurmurHash3 哈希函数

**位置**: `include/utils.h` 第133-137行

```cpp
array<uint64_t, 2> mm_hash(const uint8_t* data, size_t len) {
    array<uint64_t, 2> hash_value;
    MurmurHash3_x64_128(data, len, 0, hash_value.data());
    return hash_value;
}
```

**解释**:
- **MurmurHash3**: 快速非加密哈希函数
- **输出**: 128位 (两个64位整数)
- **用途**: 计算分区ID
- **特点**: 速度快，分布均匀，但不具备密码学安全性

#### 1.3 线程池实现

**位置**: `include/ThreadPool.h`

```cpp
class ThreadPool {
private:
    vector<thread> workers;                    // 工作线程
    queue<function<void()>> tasks;             // 任务队列
    mutex queue_mutex;                         // 队列互斥锁
    condition_variable condition;              // 条件变量
    bool stop;                                 // 停止标志

public:
    ThreadPool(size_t threads) : stop(false) {
        // 创建工作线程
        for(size_t i = 0; i < threads; ++i) {
            workers.emplace_back([this] {
                for(;;) {
                    function<void()> task;
                    {
                        unique_lock<mutex> lock(this->queue_mutex);
                        // 等待任务或停止信号
                        this->condition.wait(lock, [this] {
                            return this->stop || !this->tasks.empty();
                        });
                        if(this->stop && this->tasks.empty())
                            return;
                        task = move(this->tasks.front());
                        this->tasks.pop();
                    }
                    task();  // 执行任务
                }
            });
        }
    }

    // 添加任务到队列
    template<class F, class... Args>
    auto enqueue(F&& f, Args&&... Args) -> future<...> {
        auto task = make_shared<packaged_task<...>>(...);
        future<...> res = task->get_future();
        {
            unique_lock<mutex> lock(queue_mutex);
            tasks.emplace([task](){ (*task)(); });
        }
        condition.notify_one();  // 唤醒一个工作线程
        return res;
    }
};
```

**解释**:
- **生产者-消费者模式**: 主线程添加任务，工作线程执行任务
- **互斥锁**: 保护任务队列的并发访问
- **条件变量**: 高效的线程同步机制
- **优势**: 避免频繁创建/销毁线程的开销

#### 1.4 双线性配对计算

**位置**: `hickae.hpp` 第107-108行

```cpp
element_init_GT(gt, pairing);
element_pairing(gt, g1, g2);
```

**解释**:
- **配对函数**: e: G1 × G2 → GT
- **性质**:
  - 双线性: e(g1^a, g2^b) = e(g1, g2)^(ab)
  - 非退化: e(g1, g2) ≠ 1
- **应用**: 基于身份的加密、聚合签名等
- **计算**: 使用 PBC 库的高效实现

#### 1.5 ZeroMQ 消息传递

**服务器端** (`server.cpp`):
```cpp
zmq::context_t context(1);
zmq::socket_t socket(context, ZMQ_REP);  // REP = Reply
socket.bind("tcp://*:8888");

while(1) {
    zmq::message_t query;
    socket.recv(&query);      // 阻塞等待请求

    // 处理请求...

    zmq::message_t reply(...);
    socket.send(reply);       // 发送响应
}
```

**客户端** (`client.cpp`):
```cpp
zmq::context_t context(1);
zmq::socket_t socket(context, ZMQ_REQ);  // REQ = Request
socket.connect("tcp://127.0.0.1:8888");

zmq::message_t request(...);
socket.send(request);         // 发送请求

zmq::message_t reply;
socket.recv(&reply);          // 阻塞等待响应
```

**解释**:
- **REQ-REP 模式**: 严格的请求-响应模式
- **同步通信**: 必须先发送再接收 (或先接收再发送)
- **优势**: 简单、可靠、支持多种传输协议

### 2. C++ 高级特性使用

#### 2.1 Lambda 表达式

```cpp
threads.push_back(pool.enqueue([t, &writer_set, &gamma_t]() {
    // Lambda 函数体
    int writer_id;
    while(!writer_set.empty()) {
        mtx.lock();
        writer_id = writer_set.back();
        writer_set.pop_back();
        mtx.unlock();

        // 处理 writer_id...
    }
}));
```

**解释**:
- **语法**: `[捕获列表](参数列表) { 函数体 }`
- **捕获方式**:
  - `t`: 按值捕获
  - `&writer_set`: 按引用捕获
- **用途**: 创建匿名函数，常用于线程和回调

#### 2.2 智能指针和 RAII

```cpp
// 原始指针 (需手动管理)
int *output = new int[size];
// ... 使用 ...
delete[] output;  // 容易忘记

// 智能指针 (自动管理)
unique_ptr<int[]> output(new int[size]);
// ... 使用 ...
// 自动释放，无需 delete
```

**RAII (Resource Acquisition Is Initialization)**:
```cpp
{
    unique_lock<mutex> lock(mtx);  // 构造时加锁
    // 临界区代码
}  // 析构时自动解锁
```

#### 2.3 模板和泛型编程

```cpp
template<class F, class... Args>
auto ThreadPool::enqueue(F&& f, Args&&... args)
    -> future<typename result_of<F(Args...)>::type>
{
    using return_type = typename result_of<F(Args...)>::type;
    // ...
}
```

**解释**:
- **可变参数模板**: `Args...` 接受任意数量参数
- **完美转发**: `forward<F>(f)` 保持参数的值类别
- **类型推导**: `auto` 和 `decltype` 自动推导类型

#### 2.4 STL 容器

```cpp
// 哈希表 (O(1) 查找)
unordered_map<string, DSSE_Token> EDTkn;

// 动态数组
vector<PEKS_Token> tokens;

// 队列
queue<function<void()>> tasks;
```

**选择原则**:
- `vector`: 顺序访问、动态大小
- `unordered_map`: 快速查找、键值对
- `queue`: FIFO 操作

### 3. 密码学原理深入

#### 3.1 双线性配对的应用

**加密** (HICKAE_Encrypt):
```
c1 = g2^r
c2 = theta_G2^r
c3 = (gamma_G2 + class_binding_key[wid])^r
ut = e(H(id), delta_G2)^r
c4 = m ⊕ H(ut)
```

**解密** (HICKAE_Decrypt):
```
temp = k2 + Σ correlation[j][wid]
ut = e(temp, k1*c1 - c2) - e(k3, c3)
m = c4 ⊕ H(ut)
```

**正确性证明**:
```
e(temp, k1*c1 - c2) - e(k3, c3)
= e(k2, (alpha^tau_prime + theta)*g2^r - theta_G2^r) - e(k3, c3)
= e(k2, alpha^tau_prime * g2^r) - e(k3, c3)
= e(H(id)^delta * alpha^(-tau_prime), alpha^tau_prime * g2^r) - e(k3, c3)
= e(H(id), delta_G2)^r - e(k3, c3)
= ut  (如果 wid 匹配)
```

#### 3.2 前向安全性

**问题**: 如果服务器被攻破，攻击者能否搜索过去的查询?

**解决**: 使用一次性随机数 tau_prime
- 每次搜索生成新的 tau_prime
- 搜索令牌不可重用
- 即使泄露当前令牌，也无法搜索其他关键词

#### 3.3 多写者聚合

**挑战**: 如何用一个令牌搜索多个写者的数据?

**方案**: 使用关联值 (correlation)
```cpp
correlation[i][j] = g1^(alpha^(tau + sigma_class[i] - sigma_class[j]))
```

**作用**: 将写者 j 的密文"转换"为写者 i 的密文
```
temp = k2 + correlation[j][wid]
```

这样，一个聚合令牌可以解密所有写者的密文

---

## 学习路径建议

### 1. 初学者路径 (C++ 基础薄弱)

**第一阶段: C++ 基础** (1-2周)
1. 学习 C++ 基本语法 (变量、函数、类)
2. 理解指针和引用
3. 掌握 STL 容器 (vector, map, unordered_map)
4. 学习文件 I/O 和字符串处理

**推荐资源**:
- 《C++ Primer》
- cppreference.com
- learncpp.com

**第二阶段: 项目结构理解** (1周)
1. 阅读 `README.md`
2. 查看 `config.hpp` 和 `types.hpp`
3. 理解 Makefile 编译流程
4. 运行示例程序

**第三阶段: 核心代码阅读** (2-3周)
1. 从 `main` 函数开始
2. 跟踪搜索流程 (client → server → client)
3. 理解数据结构 (PEKS_Token, DSSE_Token)
4. 分析加密/解密函数

**第四阶段: 密码学理论** (2-4周)
1. 学习对称加密 (AES)
2. 理解哈希函数 (SHA-512)
3. 学习双线性配对基础
4. 阅读 Hermes 论文

### 2. 进阶路径 (有 C++ 基础)

**第一阶段: 快速上手** (3-5天)
1. 编译并运行项目
2. 阅读核心头文件
3. 理解客户端-服务器交互
4. 修改配置参数并观察效果

**第二阶段: 深入理解** (1-2周)
1. 详细阅读 HICKAE 实现
2. 分析搜索和更新流程
3. 理解分区和时期管理
4. 研究多线程实现

**第三阶段: 论文研读** (1-2周)
1. 阅读 Hermes 论文
2. 对照代码理解算法
3. 分析安全性证明
4. 比较标准模式和 Hermes+

**第四阶段: 扩展实验** (2-4周)
1. 修改加密方案参数
2. 实现新的优化策略
3. 测试不同数据集
4. 性能分析和调优

### 3. 专家路径 (研究导向)

**第一阶段: 全面理解** (1周)
1. 通读所有代码
2. 理解每个函数的作用
3. 掌握系统架构
4. 识别关键优化点

**第二阶段: 理论深化** (2-3周)
1. 深入学习双线性配对密码学
2. 研究可搜索加密理论
3. 阅读相关论文 (DSSE, PEKS)
4. 理解安全模型和证明

**第三阶段: 创新研究** (持续)
1. 识别系统局限性
2. 提出改进方案
3. 实现新功能
4. 撰写研究论文

### 4. 实践项目建议

**初级项目**:
1. 添加日志功能，记录所有操作
2. 实现简单的 GUI 界面
3. 支持删除操作 (目前只支持添加)
4. 添加统计功能 (查询次数、平均延迟等)

**中级项目**:
1. 实现持久化存储 (将索引保存到磁盘)
2. 支持范围查询 (例如: 查找包含多个关键词的文档)
3. 优化内存使用 (使用内存映射文件)
4. 实现访问控制 (不同用户有不同权限)

**高级项目**:
1. 实现分布式服务器 (多台服务器协同)
2. 支持动态添加/删除写者
3. 实现更高效的分区策略
4. 研究抗量子攻击的加密方案

---

## 调试技巧

### 1. 使用 GDB 调试

```bash
# 编译时添加调试信息
cd Hermes
make clean
CFLAGS="-g -O0" make

# 启动 GDB
cd server
gdb ./server

# GDB 命令
(gdb) break main              # 在 main 函数设置断点
(gdb) break hickae.hpp:240    # 在特定行设置断点
(gdb) run 25                  # 运行程序 (25个写者)
(gdb) next                    # 单步执行
(gdb) print writer_id         # 打印变量
(gdb) backtrace               # 查看调用栈
(gdb) continue                # 继续执行
```

### 2. 添加调试输出

```cpp
// 在关键位置添加输出
cout << "[DEBUG] writer_id = " << writer_id << endl;
cout << "[DEBUG] keyword = " << keyword << endl;

// 输出十六进制数据
for(int i = 0; i < 32; ++i)
    printf("%02x ", token[i]);
printf("\n");

// 输出大整数
mpz_out_str(stdout, 10, alpha);
printf("\n");
```

### 3. 使用 Valgrind 检测内存泄漏

```bash
# 安装 Valgrind
sudo apt-get install valgrind

# 检测内存泄漏
cd server
valgrind --leak-check=full ./server 25

# 输出示例
# ==12345== LEAK SUMMARY:
# ==12345==    definitely lost: 0 bytes in 0 blocks
# ==12345==    indirectly lost: 0 bytes in 0 blocks
```

### 4. 性能分析

```bash
# 使用 perf 工具
sudo apt-get install linux-tools-common

# 记录性能数据
cd server
perf record -g ./server 25

# 在另一个终端运行客户端
cd client
./client -s university 25

# 分析性能数据
perf report

# 查看热点函数
# Overhead  Command  Shared Object     Symbol
#   45.23%  server   server            [.] HICKAE_Decrypt
#   23.45%  server   libpbc.so         [.] element_pairing
#   12.34%  server   libcrypto.so      [.] SHA512_Update
```

---

## 扩展阅读

### 1. 相关论文

**可搜索加密**:
- "Practical Techniques for Searches on Encrypted Data" (Song et al., 2000)
- "Dynamic Searchable Encryption via Blind Storage" (Kamara et al., 2014)

**双线性配对**:
- "Identity-Based Encryption from the Weil Pairing" (Boneh & Franklin, 2001)
- "Pairing-Based Cryptography at High Security Levels" (NIST, 2012)

**多写者加密数据库**:
- "Hermes: Efficient and Secure Multi-Writer Encrypted Database" (Le & Hoang, 2025)

### 2. 开源项目

**类似项目**:
- OpenSSE (https://github.com/OpenSSE)
- Clusion (https://github.com/encryptedsystems/Clusion)

**密码学库**:
- PBC Library (https://crypto.stanford.edu/pbc/)
- RELIC Toolkit (https://github.com/relic-toolkit/relic)

### 3. 在线资源

**C++ 学习**:
- cppreference.com
- isocpp.org
- stackoverflow.com

**密码学学习**:
- Coursera: Cryptography I (Stanford)
- crypto.stanford.edu
- eprint.iacr.org

---

## 总结

Hermes 项目是一个复杂但设计精良的加密数据库系统，涉及多个领域的知识:

1. **C++ 编程**: 面向对象、模板、多线程、STL
2. **密码学**: 对称加密、哈希、双线性配对、可搜索加密
3. **系统设计**: 客户端-服务器架构、索引结构、性能优化
4. **网络编程**: ZeroMQ 消息传递、序列化/反序列化

**学习建议**:
- 循序渐进，从简单到复杂
- 动手实践，运行和修改代码
- 结合论文，理解理论基础
- 多做实验，观察系统行为

**应用价值**:
- 云存储隐私保护
- 医疗数据安全共享
- 金融数据加密查询
- 物联网数据安全

希望这份文档能帮助您深入理解 Hermes 项目！如有疑问，欢迎查阅代码注释或联系项目作者。

---

**文档版本**: 1.0
**最后更新**: 2025-11-09
**作者**: AI Assistant
**项目地址**: https://github.com/vt-asaplab/Hermes


