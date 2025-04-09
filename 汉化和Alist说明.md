# Mirror-Leech-Telegram-Bot 汉化和Alist集成

本项目基于原版 Mirror-Leech-Telegram-Bot 进行了汉化和功能增强。

## 汉化内容

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
