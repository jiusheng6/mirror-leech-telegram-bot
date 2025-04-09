#!/bin/bash

# 启动 Alist
echo "正在启动 Alist..."
cd /usr/src/alist
# 在后台运行 Alist
./alist server > /dev/null 2>&1 &
cd /usr/src/app

# 启动机器人
source mltbenv/bin/activate
python3 update.py
python3 -m bot
