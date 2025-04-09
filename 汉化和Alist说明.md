# Mirror-Leech-Telegram-Bot 汉化和Alist集成

本文档记录了对项目的汉化内容及后续可能需要改进的地方。

## 已完成的汉化

1. **用户界面按钮**
   - 所有帮助菜单按钮已汉化（例如："New-Name" → "重命名"，"DL-Auth" → "下载认证"等）
   - 通用UI按钮已汉化（例如："Select Files" → "选择文件"，"Done Selecting" → "选择完成"等）
   - 关闭按钮已汉化（"Close" → "关闭"）
   - Telegraph查看按钮已汉化（"VIEW" → "查看"）

2. **错误消息**
   - 私人链接访问错误已汉化
   - 聊天访问权限提示已汉化

3. **状态消息**
   - 任务状态已汉化（例如："Upload" → "上传"，"Download" → "下载"等）
   - 时间单位已汉化（例如："days" → "天"，"hours" → "小时"等）

## 可能需要进一步汉化的内容

1. **命令说明**
   可能还有一些命令说明未完全汉化，建议将来更新时重点关注。

2. **错误和提示消息**
   部分错误和提示消息可能依然是英文，使用过程中可记录，以便后续更新。

3. **Web界面元素**
   Web界面（如qBittorrent、JDownloader等）的界面元素可能仍然是英文，这些通常需要通过各自应用进行设置。

## 汉化更新方法

如果您发现有未汉化的内容或翻译需要改进，可以：

1. 直接编辑对应的源代码文件
2. 主要汉化文件位于：
   - `bot/helper/ext_utils/help_messages.py`（帮助信息和按钮标签）
   - `bot/helper/ext_utils/bot_utils.py`（UI按钮和功能）
   - `bot/helper/ext_utils/status_utils.py`（状态信息）
   - `bot/helper/telegram_helper/message_utils.py`（消息和错误提示）

完成编辑后使用以下命令提交更改：
```bash
git add .
git commit -m "更新汉化内容"
git push
```

## Alist 管理员信息

- 默认访问地址：`http://你的IP:5244`
- 用户名：`admin`
- 密码：`admin123456`

1. 汉化了`help_messages.py`文件，包含了大部分命令和帮助文本
2. 汉化了`status_utils.py`文件，包含了状态显示相关的文本
3. 汉化了`status.py`文件，包含了状态界面的文本

## Alist集成

1. 修改了`Dockerfile`，添加了Alist的安装步骤
   - 安装的Alist版本: v3.44.0
   - 安装路径: /usr/src/alist

2. 修改了`start.sh`，添加了Alist的启动命令
   - Alist将作为后台服务运行
   - 默认端口为5244

## 如何提交更改到Git

我们已经准备了脚本来帮助您将这些更改提交到Git仓库：

### Windows用户

直接运行`git_commit.bat`文件：

```
git_commit.bat
```

### Linux/macOS用户

使用以下命令运行脚本：

```bash
chmod +x git_commit.sh
./git_commit.sh
```

## 注意事项

- Alist的默认访问地址为: http://yourserver:5244
- 首次使用Alist时，需要使用随机生成的密码登录，请查看容器日志获取密码
- 您可以修改`Dockerfile`来自定义Alist的安装版本

感谢使用本项目！
