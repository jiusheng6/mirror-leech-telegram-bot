#!/bin/bash

# 启动 Alist
echo "正在启动 Alist..."
cd /usr/src/alist

# 在后台运行 Alist
./alist server --data /usr/src/alist/data > /dev/null 2>&1 &

# 等待 Alist 完全启动
sleep 5

# 获取管理员信息
echo "Alist 已启动，初始管理员信息:"
./alist admin info

# 返回主工作目录
cd /usr/src/app

# 启动机器人
echo "正在启动 Mirror-Leech-Telegram-Bot..."
source mltbenv/bin/activate
python3 update.py
python3 -m bot
