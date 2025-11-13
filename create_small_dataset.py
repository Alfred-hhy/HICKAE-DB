#!/usr/bin/env python3
"""
创建小型测试数据集
用于快速测试和立项演示
"""

import os
import random

# 配置参数
NUM_WRITERS = 25  # 写者数量（增加到 25，接近默认配置）
KEYWORDS_PER_WRITER = 150  # 每个写者的关键词数量（增加到 150）
DOCS_PER_KEYWORD_MIN = 5  # 每个关键词最少文档数（增加到 5）
DOCS_PER_KEYWORD_MAX = 20  # 每个关键词最多文档数（增加到 20）

# 常用关键词列表（模拟真实场景）
COMMON_KEYWORDS = [
    # 技术类
    "database", "security", "encryption", "network", "system", "server", "client",
    "algorithm", "protocol", "authentication", "authorization", "privacy", "data",
    "search", "query", "index", "storage", "backup", "recovery", "performance",
    
    # 业务类
    "project", "meeting", "report", "document", "presentation", "proposal",
    "contract", "agreement", "invoice", "payment", "budget", "schedule",
    "deadline", "milestone", "deliverable", "requirement", "specification",
    
    # 通用类
    "email", "message", "notification", "alert", "update", "status", "progress",
    "issue", "problem", "solution", "question", "answer", "discussion", "review",
    "approval", "feedback", "comment", "note", "memo", "reminder", "task",
    
    # 学术类
    "research", "paper", "publication", "conference", "journal", "experiment",
    "analysis", "result", "conclusion", "methodology", "literature", "citation",
    "hypothesis", "theory", "model", "framework", "evaluation", "validation",
    
    # 组织类
    "department", "team", "manager", "director", "employee", "staff", "member",
    "organization", "company", "enterprise", "business", "corporate", "office",
    "division", "branch", "headquarters", "subsidiary", "partner", "vendor",
    
    # 其他
    "university", "college", "student", "professor", "course", "lecture", "exam",
    "grade", "degree", "certificate", "training", "workshop", "seminar", "tutorial"
]

def create_small_dataset():
    """创建小型数据集"""
    
    # 创建输出目录
    output_dir = "database_small"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"✓ 创建目录: {output_dir}/")
    
    # 为每个写者创建数据库文件
    for writer_id in range(1, NUM_WRITERS + 1):
        filename = os.path.join(output_dir, f"{writer_id}.txt")
        
        # 随机选择关键词
        selected_keywords = random.sample(COMMON_KEYWORDS, 
                                         min(KEYWORDS_PER_WRITER, len(COMMON_KEYWORDS)))
        
        with open(filename, 'w') as f:
            for keyword in selected_keywords:
                # 为每个关键词生成随机的文档ID列表
                num_docs = random.randint(DOCS_PER_KEYWORD_MIN, DOCS_PER_KEYWORD_MAX)
                doc_ids = random.sample(range(1, 1000), num_docs)
                doc_ids.sort()
                
                # 写入格式: keyword doc_id1 doc_id2 ...
                f.write(f"{keyword} {' '.join(map(str, doc_ids))}\n")
        
        print(f"✓ 创建文件: {filename} ({len(selected_keywords)} 个关键词)")
    
    print(f"\n✓ 成功创建 {NUM_WRITERS} 个数据库文件")
    print(f"  - 每个文件约 {KEYWORDS_PER_WRITER} 个关键词")
    print(f"  - 每个关键词 {DOCS_PER_KEYWORD_MIN}-{DOCS_PER_KEYWORD_MAX} 个文档")
    print(f"\n数据集位置: {output_dir}/")

if __name__ == "__main__":
    create_small_dataset()

