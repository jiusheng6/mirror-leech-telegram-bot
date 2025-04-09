@echo off
echo 正在添加修改的文件...
git add bot/helper/ext_utils/help_messages.py bot/helper/ext_utils/status_utils.py bot/modules/status.py Dockerfile start.sh
echo 正在提交更改...
git commit -m "汉化项目UI和添加Alist功能

1. 汉化了help_messages.py文件，包含了大部分命令和帮助文本
2. 汉化了status_utils.py文件，包含了状态显示相关的文本
3. 汉化了status.py文件，包含了状态界面的文本
4. 修改了Dockerfile，添加了Alist的安装步骤
5. 修改了start.sh，添加了Alist的启动命令"
echo 推送到远程仓库...
git push
echo 完成！
