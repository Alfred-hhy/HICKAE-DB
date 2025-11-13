#!/bin/bash
# 切换到小数据集的脚本

echo "正在切换到小数据集..."

# 备份原始文件
if [ ! -f "Hermes/server/server.cpp.backup" ]; then
    cp Hermes/server/server.cpp Hermes/server/server.cpp.backup
    echo "✓ 备份 Hermes/server/server.cpp"
fi

if [ ! -f "Hermes/client/client.cpp.backup" ]; then
    cp Hermes/client/client.cpp Hermes/client/client.cpp.backup
    echo "✓ 备份 Hermes/client/client.cpp"
fi

# 修改 server.cpp 使用小数据集
sed -i 's|"../database/"|"../../database_small/"|g' Hermes/server/server.cpp
echo "✓ 修改 Hermes/server/server.cpp 使用 database_small/"

# 修改 client.cpp 使用小数据集
sed -i 's|"../database/"|"../../database_small/"|g' Hermes/client/client.cpp
echo "✓ 修改 Hermes/client/client.cpp 使用 database_small/"

echo ""
echo "✓ 切换完成！现在使用小数据集 (database_small/)"
echo ""
echo "下一步："
echo "  1. 进入 Hermes 目录: cd Hermes"
echo "  2. 重新编译: make clean && make"
echo "  3. 运行测试: cd .. && ./benchmark.sh"

