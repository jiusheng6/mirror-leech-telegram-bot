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

# 设置固定的Alist管理员密码
echo "Alist 已启动，正在设置固定管理员密码..."
# 设置管理员密码为 admin123456
./alist admin set admin123456
echo "Alist 管理员用户名: admin"
echo "Alist 管理员密码: admin123456"
echo "请记住这些凭据用于访问 Alist 管理面板"

# 返回主工作目录
cd /usr/src/app

# 启动机器人
echo "正在启动 Mirror-Leech-Telegram-Bot..."
source mltbenv/bin/activate
python3 update.py
python3 -m bot
