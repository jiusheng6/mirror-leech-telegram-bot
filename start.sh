#!/bin/bash

# 启动 Alist
echo "正在启动 Alist..."
cd /usr/src/alist

# 确保数据目录存在
mkdir -p /usr/src/alist/data

# 在后台运行 Alist
./alist server --data /usr/src/alist/data > /dev/null 2>&1 &

# 等待 Alist 完全启动
sleep 5

# 获取管理员信息
echo "Alist 已启动，正在获取/重置管理员密码:"
# 尝试查看信息，如果没有输出密码，则重置为随机密码
ADMIN_INFO=$(./alist admin info)
if echo "$ADMIN_INFO" | grep -q "password can only be output at the first startup"; then
    echo "Alist 密码已被存储为哈希值，正在重置为新的随机密码..."
    ./alist admin random
else
    echo "$ADMIN_INFO"
fi

# 返回主工作目录
cd /usr/src/app

# 启动机器人
echo "正在启动 Mirror-Leech-Telegram-Bot..."
source mltbenv/bin/activate
python3 update.py
python3 -m bot
