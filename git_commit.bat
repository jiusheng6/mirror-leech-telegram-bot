@echo off
echo 正在添加修改的文件...
git add bot\helper\ext_utils\help_messages.py
git add bot\helper\ext_utils\status_utils.py
git add bot\modules\status.py
git add Dockerfile
git add start.sh
git add README.md
git add config_sample.py
git add 安装指南.md
git add 完成工作总结.md

echo 正在提交更改...
git commit -m "汉化项目UI并集成Alist文件管理系统

1. 汉化了help_messages.py文件，包含了大部分命令和帮助文本
2. 汉化了status_utils.py文件，包含了状态显示相关的文本
3. 汉化了status.py文件，包含了状态界面的文本
4. 修改了Dockerfile，使用curl下载安装Alist，添加了数据卷
5. 修改了start.sh，优化Alist启动流程，自动重置随机密码
6. 汉化了README.md，提供完整的中文文档
7. 汉化了config_sample.py，提供详细的中文注释
8. 添加了中文安装指南，包含数据持久化说明
9. 解决了构建过程中的依赖问题"

echo 推送到远程仓库...
git push

echo 完成！
