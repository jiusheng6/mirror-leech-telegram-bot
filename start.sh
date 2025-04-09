#!/bin/bash

# 启动 Alist
echo "正在启动 Alist..."
cd /usr/src/alist
# 在后台运行 Alist，并将密码信息输出到日志
./alist server > /var/log/alist.log 2>&1 &
# 等待 Alist 完全启动
sleep 3
# 输出初始管理员信息以便查看
echo "Alist 已启动，初始管理员信息:"
grep -A 2 "初始管理员信息" /var/log/alist.log || echo "无法获取管理员信息，请查看完整日志"
cd /usr/src/app

# 启动机器人
echo "正在启动 Mirror-Leech-Telegram-Bot..."
source mltbenv/bin/activate
python3 update.py
python3 -m bot
